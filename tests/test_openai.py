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
    "input,expected",
    (
        ("Hello world", "Hello world"),
        ("<p>Hello world</p>", "Hello world"),
    ),
)
async def test_strip_tags(input, expected):
    ds = Datasette(memory=True)
    response = await ds.client.get(
        "/_memory.json",
        params={
            "sql": "select openai_strip_tags(:text)",
            "text": input,
            "_shape": "arrayfirst",
        },
    )
    assert response.status_code == 200
    assert response.json() == [expected]
