"""Main function app"""
from __future__ import annotations

import logging

import azure.functions as func

from func_parse_report import parse_func
from func_query import query_func

LOGGER = logging.getLogger(__name__)

app = func.FunctionApp()

app.register_functions(parse_func)
app.register_functions(query_func)
