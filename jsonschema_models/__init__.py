"""JSON Schema models library."""

from importlib import metadata

from jsonschema_models.models import (
    ArraySchema,
    BooleanSchema,
    ContentSchema,
    FormatAnnotation,
    IntegerSchema,
    NullSchema,
    NumberSchema,
    ObjectSchema,
    Reference,
    Schema,
    SchemaType,
    StringSchema,
)

__all__ = [
    'ArraySchema',
    'BooleanSchema',
    'ContentSchema',
    'FormatAnnotation',
    'IntegerSchema',
    'NullSchema',
    'NumberSchema',
    'ObjectSchema',
    'Reference',
    'Schema',
    'SchemaType',
    'StringSchema',
    'version',
]

try:
    version = metadata.version('jsonschema-models')
except metadata.PackageNotFoundError:  # pragma: nocover
    version = '0.0.0.dev0'  # Default development version
