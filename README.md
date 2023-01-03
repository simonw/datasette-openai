# datasette-openai

[![PyPI](https://img.shields.io/pypi/v/datasette-openai.svg)](https://pypi.org/project/datasette-openai/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-openai?include_prereleases&label=changelog)](https://github.com/simonw/datasette-openai/releases)
[![Tests](https://github.com/simonw/datasette-openai/workflows/Test/badge.svg)](https://github.com/simonw/datasette-openai/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-openai/blob/main/LICENSE)

SQL functions for calling OpenAI APIs

## Installation

Install this plugin in the same environment as Datasette.

    datasette install datasette-openai

## ⚠️ Warning ⚠️

This plugin allows you to call a commercial, priced API using SQL queries.

Use this with care! You could accidentally spend a lot of money.

For example, the following query:

```sql
select
  openai_davinci(
    'Summarize this text: ' || content, 200, 1, :api_key
) as summary
from documents
```
Would execute one paid API call for every item in the `documents` database. This could become very expensive.

Be sure to familiarize yourself with [OpenAI pricing](https://openai.com/api/pricing/). You will need to obtain an [API key](https://beta.openai.com/account/api-keys).

## Usage

This extension provides three new SQL functions:

### openai_davinci(prompt, max_tokens, temperature, api_key)

This function runs a `text-davinci-003` completion against the provided prompt, with the specified values for max tokens and temperature.

Da Vinci is currently 2 cents per thousand tokens.

### openai_embedding(text, api_key)

This calls the OpenAI embedding endpoint and returns a binary object representing the floating point embedding for the provided text.

```sql
select openai_embedding(:query, :api_key)
```
An embedding is an array of 1536 floating point values. The returned value from this is a `blob` encoding of those values.

It's mainly useful for using with the `openai_embedding_similarity()` function.

The embedding API is very inexpensive: at time of writing, $0.0004 cents per thousand tokens, where a token is more-or-less a single word.

### openai_embedding_similarity(a, b)

This function does not make any API calls. It takes two embedding blobs and returns the cosine similarity between the two.

This function is particularly useful if you have stored embeddings of documents in a database table, and you want to find the most similar documents to a query or to another document.

A simple search query could look like this:
```sql
with query as (
  select
    openai_embedding(:query, :token) as q
)
select
  id,
  title,
  openai_embedding_similarity(query.q, embedding) as score
from
  content, query
order by
  score desc
limit 10
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-openai
    python3 -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
