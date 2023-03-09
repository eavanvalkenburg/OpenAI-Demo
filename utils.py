"""Utils for the openai runs."""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterable

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from pypdf import PdfReader

from const import T

LOGGER = logging.getLogger(__name__)


def open_file(filepath):
    """Open the file and return the text."""
    with open(filepath, "r", encoding="utf-8") as infile:
        return infile.read()


def open_json(filepath: str) -> Any:
    """Open the file and read the json and return."""
    with open(filepath, "r", encoding="utf-8") as infile:
        return json.load(infile)


def open_pdf(filepath):
    """Read the pdf and run extract pages."""
    reader = PdfReader(filepath)
    return extract_pages_pdf(reader)


def extract_pages_pdf(reader):
    """Extract the pages from the pdf"""
    alltext = ""
    for page in reader.pages:
        alltext += page.extract_text()
    return alltext


def save_file(content, filepath):
    """Save the content to the file."""
    with open(filepath, "w", encoding="utf-8") as outfile:
        outfile.write(content)


def save_list(content, filepath):
    """Parse the list and call the save file function."""
    str_list = ",".join(str(x) for x in content)
    save_file(str_list, filepath)


async def desync(items: list[T]) -> AsyncIterable[T]:
    """Desync the iterator."""
    for item in items:
        yield item


async def write_cosmos_item(
    record: dict[str, Any],
    database_name: str,
    collection_name: str,
    connection_string: str | None,
):
    """Write the dataframe to cosmosdb."""
    if not connection_string:
        raise ValueError("Connection string is not set")
    async with CosmosClient.from_connection_string(connection_string) as client:
        database = client.get_database_client(database=database_name)
        collection = database.get_container_client(collection_name)
        LOGGER.debug("Writing to cosmosdb: %s", record)
        try:
            await collection.upsert_item(record)
        except exceptions.CosmosHttpResponseError as e:
            LOGGER.error(e)
            raise e


async def get_cosmos_items(
    database_name: str,
    collection_name: str,
    connection_string: str | None,
    partition_key: str | None = None,
) -> AsyncIterable[dict[str, Any]]:
    """Get the items from cosmosdb."""
    if not connection_string:
        raise ValueError("Connection string is not set")
    async with CosmosClient.from_connection_string(connection_string) as client:
        database = client.get_database_client(database=database_name)
        collection = database.get_container_client(collection_name)
        LOGGER.debug("Getting items from cosmosdb: %s", collection)
        query = "SELECT * FROM c"
        if partition_key:
            items = collection.query_items(query=query, partition_key=partition_key)
        else:
            items = collection.query_items(query=query)
        async for item in items:
            yield item
