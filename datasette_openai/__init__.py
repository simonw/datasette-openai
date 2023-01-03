from datasette import hookimpl
import httpx
import struct


@hookimpl
def prepare_connection(conn):
    conn.create_function("openai_embedding", 2, openai_embedding)
    conn.create_function("openai_embedding_similarity", 2, openai_embedding_similarity)
    conn.create_function("openai_davinci", 4, openai_davinci)


def openai_embedding(text, api_key):
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "input": text,
            "model": "text-embedding-ada-002",
        },
    )
    response.raise_for_status()
    return encode(response.json()["data"][0]["embedding"])


def openai_embedding_similarity(embedding, compare_to_embedding):
    return cosine_similarity(decode(embedding), decode(compare_to_embedding))


def openai_davinci(prompt, max_tokens, temperature, api_key):
    response = httpx.post(
        "https://api.openai.com/v1/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "text-davinci-003",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["text"]


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5
    return dot_product / (magnitude_a * magnitude_b)


def decode(blob):
    return struct.unpack("f" * 1536, blob)


def encode(values):
    return struct.pack("f" * 1536, *values)
