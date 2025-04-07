from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

import config
from database import get_db_tables_schema

template = """
## Given the following SQL tables:
{tables}

## Create a valid SQL query that does the following:
{user_input}

## For provided table definitions, create complex `JOIN` queries, subqueries, or conditional aggregations.

## To validate the query do the following tasks:
1. Verify that the columns exist in the referenced tables.
2. If the query is not correct provide a different one.

## Finally, respond only with one SQL command.
"""

model_url = config.MODEL_URL
if model_url is None:
    raise Exception("Missing required MODEL_URL env variable.")

# TODO: add the base_url parameter
llm = OpenAI(base_url=model_url, api_key="not-needed", temperature=0.1)
prompt_template = PromptTemplate.from_template(template)


def generate_query(user_input: str):
    table_definitions = get_db_tables_schema()
    # TODO: add parameters
    prompt = prompt_template.invoke(
        {"tables": table_definitions, "user_input": user_input}
    )
    return llm.invoke(prompt)