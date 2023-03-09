from typing import TypeVar

T = TypeVar("T")
CHUNK_SIZE: int = 4000
MAX_RETRY: int = 5
EMBEDDING_ENCODING = "cl100k_base"
COLUMN_NAME_CONTENT = "content"
COLUMN_NAME_COMPANY = "company"
COLUMN_NAME_ID = "id"
COLUMN_NAME_EMBEDDING = "embedding"
COLUMN_NAME_SIMILARITIES = "similarities"
DATABASE_NAME = "openaidemo"
COLLECTION_NAME = "embeddings"
PARTITON_KEY = "company"
NUM_RECORDS_QUERY = 5

SUMMARIZE_PROMPT: str = r"""Write a concise summary of the following:


<<SUMMARY>>


CONCISE SUMMARY:"""

ANSWER_PROMPT: str = r"""Based on this information:

<<<CONTEXT>>>

Answer the following question, if you don't know, then say so, if there is no time specified use 2022 as the year

<<<QUERY>>>

let's take it step by step:
"""
