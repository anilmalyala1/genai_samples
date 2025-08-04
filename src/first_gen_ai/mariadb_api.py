from __future__ import annotations

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from functools import lru_cache
from typing import Any
import os

load_dotenv(find_dotenv())


class QueryRequest(BaseModel):
    """Schema for incoming natural language questions."""

    question: str


def _build_connection_uri() -> str:
    """Construct a SQLAlchemy connection string for MariaDB.

    The credentials are loaded from environment variables to avoid checking
    secrets into source control.
    """

    host = os.getenv("MARIADB_HOST", "localhost")
    port = os.getenv("MARIADB_PORT", "3306")
    user = os.getenv("MARIADB_USER")
    password = os.getenv("MARIADB_PASSWORD")
    database = os.getenv("MARIADB_DATABASE")
    return f"mariadb+pymysql://{user}:{password}@{host}:{port}/{database}"


@lru_cache
def _get_db_and_chain() -> tuple[SQLDatabase, Any]:
    """Create and cache the database and query chain."""

    db = SQLDatabase.from_uri(_build_connection_uri())
    llm = ChatOpenAI()
    chain = create_sql_query_chain(llm, db)
    return db, chain


def run_query(question: str) -> str:
    """Use an LLM to translate a natural language question to SQL and execute it."""

    db, chain = _get_db_and_chain()
    sql = chain.invoke({"question": question})
    return db.run(sql)


app = FastAPI()


@app.post("/query")
def query_db(request: QueryRequest) -> dict[str, str]:
    """Endpoint consumed by the React UI to query the database via LLM."""

    try:
        result = run_query(request.question)
    except Exception as exc:  # pragma: no cover - defensive programming
        raise HTTPException(status_code=500, detail=str(exc))
    return {"result": result}
