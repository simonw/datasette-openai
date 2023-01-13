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


@pytest.mark.asyncio
async def test_openai_build_prompt():
    ds = Datasette(memory=True)
    await ds.invoke_startup()
    db = ds.add_memory_database("test")
    await db.execute_write_script(
        """
    create table texts (id integer primary key, text text);
    insert into texts (text) values ('One');
    insert into texts (text) values ('Two tokens');
    insert into texts (text) values ('Now three tokens');
    insert into texts (text) values ('This has four tokens');
    insert into texts (text) values ('This one has five tokens');
    insert into texts (text) values ('And this one has six tokens');
    """
    )
    response = await ds.client.get(
        "/test.json",
        params={
            "sql": """
                select openai_build_prompt(
                    text,
                    "Prefix",
                    "Suffix",
                    50
                )
                from texts
            """,
            "_shape": "arrayfirst",
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        "Prefix One Two tokens Now three tokens This has four tokens This one has five tokens And this one has six tokens Suffix"
    ]
