"""Serializers — Mongo docs → JSON-safe dicts for APIs."""
from .selectors import serialize


def record_to_json(doc):
    return serialize(doc)


def records_to_json(docs):
    return [serialize(d) for d in docs]
