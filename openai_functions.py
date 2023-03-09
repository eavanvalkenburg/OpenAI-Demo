"""All the openai related functions in one."""
from __future__ import annotations

import asyncio
import logging
import os
import re
import textwrap

import openai
import pandas as pd
from openai.embeddings_utils import aget_embedding, cosine_similarity

from const import (
    ANSWER_PROMPT,
    CHUNK_SIZE,
    COLUMN_NAME_COMPANY,
    COLUMN_NAME_CONTENT,
    COLUMN_NAME_EMBEDDING,
    COLUMN_NAME_ID,
    COLUMN_NAME_SIMILARITIES,
    MAX_RETRY,
    NUM_RECORDS_QUERY,
    SUMMARIZE_PROMPT,
)
from utils import desync, write_cosmos_item

openai.api_key = os.environ["OPENAI_API_KEY"]
openai.api_base = os.environ["OPENAI_API_BASE"]
openai.api_type = os.environ["OPENAI_API_TYPE"]
openai.api_version = os.environ["OPENAI_API_VERSION"]
deployment_id_summarize = os.environ["OPENAI_DEPLOYMENT_ID_SUMMARIZE"]
deployment_id_embeddings = os.environ["OPENAI_DEPLOYMENT_ID_EMBEDDINGS"]

LOGGER = logging.getLogger(__name__)


async def gpt3_completion(
    prompt: str,
    engine: str = deployment_id_summarize,
    temp: float = 0.6,
    top_p: float = 1.0,
    tokens: int = 2000,
    freq_pen: float = 0.25,
    pres_pen: float = 0.0,
    stop: list[str] = ["<<END>>"],
) -> str:
    """Get the completion from Azure OpenAI."""
    retry = 0
    while True:
        try:
            response = await openai.Completion.acreate(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop,
            )
            text = response["choices"][0]["text"].strip()  # type: ignore
            text = re.sub("\s+", " ", text)
            LOGGER.debug("PROMPT: %s", prompt)
            LOGGER.debug("RESPONSE: %s", text)
            return text
        except Exception as exc:
            retry += 1
            if retry >= MAX_RETRY:
                return f"GPT3 error: {exc}"
            LOGGER.error("Error communicating with OpenAI: %s", exc)
            await asyncio.sleep(6)


async def summarizer(company: str, year: str, text: str) -> None:
    """Main running parsing the documents and writing the summaries and embeddings to cosmos."""
    base_prompt = SUMMARIZE_PROMPT
    chunks = textwrap.wrap(text, CHUNK_SIZE)
    index = 0
    async for chunk in desync(chunks):
        prompt = base_prompt.replace("<<SUMMARY>>", chunk)
        prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
        summary = await gpt3_completion(prompt)
        content = f"Company: {company}; Year: {year}; Content: {summary.strip()}"
        res = {
            COLUMN_NAME_ID: f"{company}_{year}_{index}",
            COLUMN_NAME_COMPANY: company,
            COLUMN_NAME_CONTENT: content,
            COLUMN_NAME_EMBEDDING: await aget_embedding(
                content, engine=deployment_id_embeddings
            ),
        }
        await write_cosmos_item(
            res,
            os.environ["databaseId"],
            os.environ["containerId"],
            os.environ["CosmosDB"],
        )
        index += 1


async def search_summaries(query: str, embedding_df: pd.DataFrame) -> str:
    """Get the similarity between the query and the embeddings."""
    embedding = await aget_embedding(query, engine=deployment_id_embeddings)
    embedding_df[COLUMN_NAME_SIMILARITIES] = embedding_df[COLUMN_NAME_EMBEDDING].apply(
        lambda x: cosine_similarity(x, embedding)
    )
    res = embedding_df.sort_values(COLUMN_NAME_SIMILARITIES, ascending=False).head(
        NUM_RECORDS_QUERY
    )
    prompt = ANSWER_PROMPT.replace("<<<QUERY>>>", query)
    prompt = prompt.replace(
        "<<<CONTEXT>>>", res[COLUMN_NAME_CONTENT].to_csv(header=False, index=False)
    )
    prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
    return await gpt3_completion(prompt)
