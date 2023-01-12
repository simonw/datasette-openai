from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-openai" in installed_plugins


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function,input,expected",
    (
        # openai_strip_tags
        ("openai_strip_tags", "Hello world", "Hello world"),
        ("openai_strip_tags", "<p>Hello world</p>", "Hello world"),
        # openai_count_tokens
        ("openai_count_tokens", "Hello world", 2),
        ("openai_count_tokens", "Hello world!", 3),
        # openai_tokenize
        ("openai_tokenize", "Hello world", '["Hello", "world"]'),
        ("openai_tokenize", "Hello world!", '["Hello", "world", "!"]'),
    ),
)
async def test_simple_functions(function, input, expected):
    ds = Datasette(memory=True)
    response = await ds.client.get(
        "/_memory.json",
        params={
            "sql": "select {}(:text)".format(function),
            "text": input,
            "_shape": "arrayfirst",
        },
    )
    assert response.status_code == 200
    assert response.json() == [expected]
