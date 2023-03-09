"""Blob handling functions."""
from __future__ import annotations

import io
import logging

import azure.functions as func
from pypdf import PdfReader

from openai_functions import summarizer
from utils import extract_pages_pdf

parse_func = func.Blueprint()

LOGGER = logging.getLogger(__name__)


@parse_func.function_name(name="parse_report")
@parse_func.route(route="parse_report", methods=[func.HttpMethod.POST])
@parse_func.blob_input(
    arg_name="report",
    path="report/{company}-{year}.pdf",
    connection="report_storage",
    data_type=func.DataType.BINARY,
)
async def parse_report_to_embedding(
    req: func.HttpRequest, report: func.InputStream
) -> func.HttpResponse:
    """Parse the blob from pdf, summarize and create the embeddings."""
    body = req.get_json()
    LOGGER.debug("Request body: %s", body)
    company = body.get("company")
    year = body.get("year")
    LOGGER.debug(
        "Parsing report %s for company: %s, year: %s", report.name, company, year
    )
    await summarizer(
        company, year, extract_pages_pdf(PdfReader(io.BytesIO(report.read())))
    )
    return func.HttpResponse("OK")
