from datasette import hookimpl
import httpx
import json
import re
import regex
import struct

tag_re = re.compile(r"<[^>]*>")

# From https://github.com/openai/gpt-2/blob/a74da5d99abaaba920de8131d64da2862a8f213b/src/encoder.py#L53
token_re = regex.compile(
    r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
)


def tokenize(text):
    return [t.strip() for t in token_re.findall(text)]


def count_tokens(text):
    return len(tokenize(text))


class BuildPrompt:
    def __init__(self):
        self.texts = []
        self.first = True
        self.prefix = ""
        self.suffix = ""
        self.completion_tokens = 0
        self.token_limit = 0

    def step(self, text, prefix, suffix, completion_tokens, token_limit=4000):
        if self.first:
            self.first = False
            self.prefix = prefix
            self.suffix = suffix
            self.completion_tokens = completion_tokens
            self.token_limit = token_limit
        self.texts.append(text)

    def finalize(self):
        available_tokens = (
            self.token_limit
            - self.completion_tokens
            - count_tokens(self.prefix)
            - count_tokens(self.suffix)
        )
        if available_tokens < 0:
            return self.prefix + " " + self.suffix
        # Get that many tokens from each of the texts
        tokens_per_text = available_tokens // len(self.texts)
        truncated_texts = []
        for text in self.texts:
            truncated_texts.append(" ".join(tokenize(text)[:tokens_per_text]))
        return self.prefix + " " + " ".join(truncated_texts) + " " + self.suffix


@hookimpl
def prepare_connection(conn):
    conn.create_function("openai_embedding", 2, openai_embedding)
    conn.create_function("openai_embedding_similarity", 2, openai_embedding_similarity)
    conn.create_function("openai_davinci", 4, openai_davinci)
    conn.create_function("openai_strip_tags", 1, openai_strip_tags)
    conn.create_function("openai_count_tokens", 1, count_tokens)
    conn.create_function("openai_tokenize", 1, lambda s: json.dumps(tokenize(s)))
    conn.create_aggregate("openai_build_prompt", 4, BuildPrompt)
    conn.create_aggregate("openai_build_prompt", 5, BuildPrompt)


def openai_strip_tags(text):
    "A very naive tag stripping implementation but good enough for now"
    return tag_re.sub("", text)


def openai_embedding(text, api_key):
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "input": text,
            "model": "text-embedding-ada-002",
        },
    )
    if response.status_code != 200:
        return response.text
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
        timeout=15.0,
    )
    if response.status_code != 200:
        return response.text
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
