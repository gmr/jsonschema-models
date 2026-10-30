"""Pydantic models for representing JSON Schema Draft 2020-12 objects."""

from __future__ import annotations

import enum
import logging
import typing

import pydantic

LOGGER = logging.getLogger(__name__)


class BaseModel(pydantic.BaseModel):
    """Base model for JSON Schema Draft 2020-12 objects."""

    model_config = {
        'arbitrary_types_allowed': True,
        'extra': 'allow',
        'populate_by_name': True,
        'serialize_by_alias': True,
        'use_enum_values': True,
        'validate_assignment': True,
        'validate_by_alias': True,
    }

    @staticmethod
    def _set_dump_kwargs(kwargs: dict) -> None:
        kwargs['by_alias'] = True
        kwargs['exclude_none'] = True

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure aliases are used."""
        self._set_dump_kwargs(kwargs)
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs) -> str:
        """Override model_dump to ensure aliases are used."""
        self._set_dump_kwargs(kwargs)
        return super().model_dump_json(**kwargs)


class SchemaType(str, enum.Enum):
    """JSON Schema type enumeration."""

    ARRAY = 'array'
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    NULL = 'null'
    NUMBER = 'number'
    OBJECT = 'object'
    STRING = 'string'


class FormatType(str, enum.Enum):
    """JSON Schema format enumeration for string validation."""

    DATE_TIME = 'date-time'
    DATE = 'date'
    TIME = 'time'
    DURATION = 'duration'
    EMAIL = 'email'
    IDN_EMAIL = 'idn-email'
    HOSTNAME = 'hostname'
    IDN_HOSTNAME = 'idn-hostname'
    IPV4 = 'ipv4'
    IPV6 = 'ipv6'
    URI = 'uri'
    URI_REFERENCE = 'uri-reference'
    IRI = 'iri'
    IRI_REFERENCE = 'iri-reference'
    UUID = 'uuid'
    URI_TEMPLATE = 'uri-template'
    JSON_POINTER = 'json-pointer'
    RELATIVE_JSON_POINTER = 'relative-json-pointer'
    REGEX = 'regex'


class Schema(BaseModel):
    """JSON Schema Draft 2020-12 schema object."""

    schema_: str | None = pydantic.Field(default=None, alias='$schema')
    id_: str | None = pydantic.Field(default=None, alias='$id')
    title: str | None = pydantic.Field(default=None)
    description: str | None = pydantic.Field(default=None)
    default: typing.Any | None = pydantic.Field(default=None)
    deprecated: bool | None = pydantic.Field(default=None)
    read_only: bool | None = pydantic.Field(default=None, alias='readOnly')
    write_only: bool | None = pydantic.Field(default=None, alias='writeOnly')
    examples: list[typing.Any] | None = pydantic.Field(default=None)
    comment: str | None = pydantic.Field(default=None, alias='$comment')

    # Type constraints
    type: SchemaType | list[SchemaType] | None = pydantic.Field(default=None)
    enum: list[typing.Any] | None = pydantic.Field(default=None)
    const: typing.Any | None = pydantic.Field(default=None)

    # Validation keywords for numeric instances
    multiple_of: float | None = pydantic.Field(
        default=None,
        alias='multipleOf',
        gt=0,
        description='Must be greater than 0',
    )
    maximum: float | None = pydantic.Field(default=None)
    exclusive_maximum: float | None = pydantic.Field(
        default=None, alias='exclusiveMaximum'
    )
    minimum: float | None = pydantic.Field(default=None)
    exclusive_minimum: float | None = pydantic.Field(
        default=None, alias='exclusiveMinimum'
    )

    # Validation keywords for strings
    max_length: int | None = pydantic.Field(
        default=None, alias='maxLength', ge=0
    )
    min_length: int | None = pydantic.Field(
        default=None, alias='minLength', ge=0
    )
    pattern: str | None = pydantic.Field(default=None)
    format: FormatType | str | None = pydantic.Field(default=None)

    # Validation keywords for arrays
    # In draft 2020-12, items only accepts a single schema
    items: Schema | None = pydantic.Field(default=None)
    # additionalItems is deprecated in draft 2020-12, kept for backwards
    # compatibility
    additional_items: bool | Schema | None = pydantic.Field(
        default=None, alias='additionalItems', deprecated=True
    )
    max_items: int | None = pydantic.Field(
        default=None, alias='maxItems', ge=0
    )
    min_items: int | None = pydantic.Field(
        default=None, alias='minItems', ge=0
    )
    unique_items: bool | None = pydantic.Field(
        default=None, alias='uniqueItems'
    )
    contains: Schema | None = pydantic.Field(default=None)
    min_contains: int | None = pydantic.Field(
        default=None, alias='minContains', ge=1
    )
    max_contains: int | None = pydantic.Field(
        default=None, alias='maxContains', ge=1
    )

    # Validation keywords for objects
    max_properties: int | None = pydantic.Field(
        default=None, alias='maxProperties', ge=0
    )
    min_properties: int | None = pydantic.Field(
        default=None, alias='minProperties', ge=0
    )
    required: list[str] | None = pydantic.Field(default=None)
    properties: dict[str, Schema] | None = pydantic.Field(default=None)
    pattern_properties: dict[str, Schema] | None = pydantic.Field(
        default=None, alias='patternProperties'
    )
    additional_properties: bool | Schema | None = pydantic.Field(
        default=None, alias='additionalProperties'
    )
    property_names: Schema | None = pydantic.Field(
        default=None, alias='propertyNames'
    )

    # Unevaluated instance keywords
    unevaluated_items: bool | Schema | None = pydantic.Field(
        default=None, alias='unevaluatedItems'
    )
    unevaluated_properties: bool | Schema | None = pydantic.Field(
        default=None, alias='unevaluatedProperties'
    )

    # Logical keywords
    all_of: list[Schema] | None = pydantic.Field(default=None, alias='allOf')
    any_of: list[Schema] | None = pydantic.Field(default=None, alias='anyOf')
    one_of: list[Schema] | None = pydantic.Field(default=None, alias='oneOf')
    not_: Schema | None = pydantic.Field(default=None, alias='not')
    if_: Schema | None = pydantic.Field(default=None, alias='if')
    then: Schema | None = pydantic.Field(default=None)
    else_: Schema | None = pydantic.Field(default=None, alias='else')

    # Conditional application keywords
    dependent_required: dict[str, list[str]] | None = pydantic.Field(
        default=None, alias='dependentRequired'
    )
    dependent_schemas: dict[str, Schema] | None = pydantic.Field(
        default=None, alias='dependentSchemas'
    )

    # Reference keywords
    ref: str | None = pydantic.Field(default=None, alias='$ref')
    defs: dict[str, Schema] | None = pydantic.Field(
        default=None, alias='$defs'
    )

    # Content keywords
    content_media_type: str | None = pydantic.Field(
        default=None, alias='contentMediaType'
    )
    content_encoding: str | None = pydantic.Field(
        default=None, alias='contentEncoding'
    )
    content_schema: Schema | None = pydantic.Field(
        default=None, alias='contentSchema'
    )

    # Vocabulary-specific keywords
    anchor: str | None = pydantic.Field(default=None, alias='$anchor')
    dynamic_anchor: str | None = pydantic.Field(
        default=None, alias='$dynamicAnchor'
    )
    dynamic_ref: str | None = pydantic.Field(default=None, alias='$dynamicRef')
    vocabulary: dict[str, bool] | None = pydantic.Field(
        default=None, alias='$vocabulary'
    )

    # Additional properties for extensibility
    extra: dict[str, typing.Any] | None = pydantic.Field(default=None)

    @pydantic.field_validator('type', mode='before')
    @classmethod
    def coerce_type(cls, value: typing.Any) -> SchemaType | list[SchemaType]:
        return coerce_type(value)

    @pydantic.model_validator(mode='after')
    def validate_contains_constraints(self) -> Schema:
        """Validate contains constraints."""
        if self.contains is not None:
            if (
                self.min_contains is not None
                and self.max_contains is not None
                and self.min_contains > self.max_contains
            ):
                raise ValueError(
                    'minContains cannot be greater than maxContains'
                )
        return self


# Specialized schema types for specific use cases
class ArraySchema(Schema):
    """Schema specifically for array types."""

    type: SchemaType = pydantic.Field(default=SchemaType.ARRAY)


class BooleanSchema(Schema):
    """Schema specifically for boolean types."""

    type: SchemaType = pydantic.Field(default=SchemaType.BOOLEAN)


class IntegerSchema(Schema):
    """Schema specifically for integer types."""

    type: SchemaType = pydantic.Field(default=SchemaType.INTEGER)


class NullSchema(Schema):
    """Schema specifically for null types."""

    type: SchemaType = pydantic.Field(default=SchemaType.NULL)


class NumberSchema(Schema):
    """Schema specifically for number types."""

    type: SchemaType = pydantic.Field(default=SchemaType.NUMBER)


class ObjectSchema(Schema):
    """Schema specifically for object types."""

    type: SchemaType = pydantic.Field(default=SchemaType.OBJECT)


class StringSchema(Schema):
    """Schema specifically for string types."""

    type: SchemaType = pydantic.Field(default=SchemaType.STRING)


# Content schema
class ContentSchema(BaseModel):
    """Content schema for string instances."""

    content_media_type: str = pydantic.Field(alias='contentMediaType')
    content_encoding: str | None = pydantic.Field(
        default=None, alias='contentEncoding'
    )
    content_schema: Schema | None = pydantic.Field(
        default=None, alias='contentSchema'
    )


# Reference
class Reference(BaseModel):
    """JSON Schema reference."""

    ref: str = pydantic.Field(alias='$ref')


# Format annotation
class FormatAnnotation(BaseModel):
    """Format annotation for string instances."""

    format: FormatType | str


# Specialized string schemas with predefined formats
class EmailSchema(StringSchema):
    """Schema for email strings."""

    format: FormatType = pydantic.Field(default=FormatType.EMAIL)


class IdnEmailSchema(StringSchema):
    """Schema for internationalized email strings."""

    format: FormatType = pydantic.Field(default=FormatType.IDN_EMAIL)


class HostnameSchema(StringSchema):
    """Schema for hostname strings."""

    format: FormatType = pydantic.Field(default=FormatType.HOSTNAME)


class IdnHostnameSchema(StringSchema):
    """Schema for internationalized hostname strings."""

    format: FormatType = pydantic.Field(default=FormatType.IDN_HOSTNAME)


class IPv4Schema(StringSchema):
    """Schema for IPv4 address strings."""

    format: FormatType = pydantic.Field(default=FormatType.IPV4)


class IPv6Schema(StringSchema):
    """Schema for IPv6 address strings."""

    format: FormatType = pydantic.Field(default=FormatType.IPV6)


class URISchema(StringSchema):
    """Schema for URI strings."""

    format: FormatType = pydantic.Field(default=FormatType.URI)


class URIReferenceSchema(StringSchema):
    """Schema for URI reference strings."""

    format: FormatType = pydantic.Field(default=FormatType.URI_REFERENCE)


class IRISchema(StringSchema):
    """Schema for IRI strings."""

    format: FormatType = pydantic.Field(default=FormatType.IRI)


class IRIReferenceSchema(StringSchema):
    """Schema for IRI reference strings."""

    format: FormatType = pydantic.Field(default=FormatType.IRI_REFERENCE)


class UUIDSchema(StringSchema):
    """Schema for UUID strings."""

    format: FormatType = pydantic.Field(default=FormatType.UUID)


class URITemplateSchema(StringSchema):
    """Schema for URI template strings."""

    format: FormatType = pydantic.Field(default=FormatType.URI_TEMPLATE)


class JsonPointerSchema(StringSchema):
    """Schema for JSON pointer strings."""

    format: FormatType = pydantic.Field(default=FormatType.JSON_POINTER)


class RelativeJsonPointerSchema(StringSchema):
    """Schema for relative JSON pointer strings."""

    format: FormatType = pydantic.Field(
        default=FormatType.RELATIVE_JSON_POINTER
    )


class RegexSchema(StringSchema):
    """Schema for regular expression strings."""

    format: FormatType = pydantic.Field(default=FormatType.REGEX)


class DateTimeSchema(StringSchema):
    """Schema for date-time strings."""

    format: FormatType = pydantic.Field(default=FormatType.DATE_TIME)


class DateSchema(StringSchema):
    """Schema for date strings."""

    format: FormatType = pydantic.Field(default=FormatType.DATE)


class TimeSchema(StringSchema):
    """Schema for time strings."""

    dformat: FormatType = pydantic.Field(default=FormatType.TIME)


class DurationSchema(StringSchema):
    """Schema for duration strings."""

    format: FormatType = pydantic.Field(default=FormatType.DURATION)


def _coerce_type(value: typing.Any) -> SchemaType:
    """Convert a specific Python type to a JSON Schema type."""
    if value is str:
        value = SchemaType.STRING
    elif value is int:
        value = SchemaType.INTEGER
    elif value is float:
        value = SchemaType.NUMBER
    elif value is bool:
        value = SchemaType.BOOLEAN
    elif value in (list, tuple):
        value = SchemaType.ARRAY
    elif value is dict:
        value = SchemaType.OBJECT
    elif value is type(None):
        value = SchemaType.NULL
    return value


def coerce_type(value: typing.Any) -> SchemaType | list[SchemaType]:
    """Translate Python types to JSON Schema types."""
    if isinstance(value, list):
        return [_coerce_type(item) for item in value]
    if not isinstance(value, SchemaType):
        return _coerce_type(value)
    return value
