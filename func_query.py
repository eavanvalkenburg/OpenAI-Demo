"""Query functions."""
from __future__ import annotations

import logging
import os
import json

import azure.functions as func
import pandas as pd

from openai_functions import search_summaries
from utils import get_cosmos_items

query_func = func.Blueprint()

LOGGER = logging.getLogger(__name__)


def test_dict(**kwargs):
    LOGGER.info("ID: %s", kwargs["id"])
    LOGGER.info("Company: %s", kwargs["company"])
    LOGGER.info("Content: %s", kwargs["content"])


@query_func.function_name(name="query")
@query_func.route(route="query/{company}", methods=[func.HttpMethod.POST])
@query_func.cosmos_db_input(
    arg_name="embeddings",
    database_name="openaidemo",
    collection_name="embeddings",
    connection_string_setting="CosmosDB",
    partition_key="{company}",
    container_name="embeddings",
)
async def query_embeddings(
    req: func.HttpRequest, embeddings: func.DocumentList
) -> func.HttpResponse:
    """Query Function"""
    body = req.get_json()
    company = req.route_params["company"].lower()
    LOGGER.debug("Request company: %s, body: %s", company, body)
    query_text = body.get("query")
    test_dict(**embeddings[0])
    embeddings_df = pd.DataFrame(embeddings)
    if embeddings_df.empty:
        return func.HttpResponse(
            "No embeddings found for company %s" % company, status_code=400
        )
    LOGGER.info(embeddings_df.head())
    answer = await search_summaries(query_text, embeddings_df)
    return func.HttpResponse(answer)
