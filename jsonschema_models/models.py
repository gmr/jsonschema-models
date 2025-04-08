"""Pydantic models for representing JSON Schema Draft 2020-12 objects."""

from __future__ import annotations

import enum
import typing

import pydantic


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


class Schema(pydantic.BaseModel):
    """JSON Schema Draft 2020-12 schema object."""

    schema_: str | None = pydantic.Field(None, alias='$schema')
    id_: str | None = pydantic.Field(None, alias='$id')
    title: str | None = None
    description: str | None = None
    default: typing.Any | None = None
    deprecated: bool | None = None
    read_only: bool | None = pydantic.Field(None, alias='readOnly')
    write_only: bool | None = pydantic.Field(None, alias='writeOnly')
    examples: list[typing.Any] | None = None
    comment: str | None = pydantic.Field(None, alias='$comment')

    # Type constraints
    type_value: SchemaType | list[SchemaType] | None = pydantic.Field(
        None, alias='type'
    )
    enum: list[typing.Any] | None = None
    const: typing.Any | None = None

    # Store Python type as a model field
    py_type: typing.Any = pydantic.Field(default=None, exclude=True)

    # Validation keywords for numeric instances
    multiple_of: float | None = pydantic.Field(
        None, alias='multipleOf', gt=0, description='Must be greater than 0'
    )
    maximum: float | None = None
    exclusive_maximum: float | None = pydantic.Field(
        None, alias='exclusiveMaximum'
    )
    minimum: float | None = None
    exclusive_minimum: float | None = pydantic.Field(
        None, alias='exclusiveMinimum'
    )

    # Validation keywords for strings
    max_length: int | None = pydantic.Field(None, alias='maxLength', ge=0)
    min_length: int | None = pydantic.Field(None, alias='minLength', ge=0)
    pattern: str | None = None
    format: FormatType | str | None = None

    # Validation keywords for arrays
    # In draft 2020-12, items only accepts a single schema
    items: Schema | None = None
    # additionalItems is deprecated in draft 2020-12, kept for backwards
    # compatibility
    additional_items: bool | Schema | None = pydantic.Field(
        None, alias='additionalItems', deprecated=True
    )
    max_items: int | None = pydantic.Field(None, alias='maxItems', ge=0)
    min_items: int | None = pydantic.Field(None, alias='minItems', ge=0)
    unique_items: bool | None = pydantic.Field(None, alias='uniqueItems')
    contains: Schema | None = None
    min_contains: int | None = pydantic.Field(None, alias='minContains', ge=1)
    max_contains: int | None = pydantic.Field(None, alias='maxContains', ge=1)

    # Validation keywords for objects
    max_properties: int | None = pydantic.Field(
        None, alias='maxProperties', ge=0
    )
    min_properties: int | None = pydantic.Field(
        None, alias='minProperties', ge=0
    )
    required: list[str] | None = None
    properties: dict[str, Schema] | None = None
    pattern_properties: dict[str, Schema] | None = pydantic.Field(
        None, alias='patternProperties'
    )
    additional_properties: bool | Schema | None = pydantic.Field(
        None, alias='additionalProperties'
    )
    property_names: Schema | None = pydantic.Field(None, alias='propertyNames')

    # Unevaluated instance keywords
    unevaluated_items: bool | Schema | None = pydantic.Field(
        None, alias='unevaluatedItems'
    )
    unevaluated_properties: bool | Schema | None = pydantic.Field(
        None, alias='unevaluatedProperties'
    )

    # Logical keywords
    all_of: list[Schema] | None = pydantic.Field(None, alias='allOf')
    any_of: list[Schema] | None = pydantic.Field(None, alias='anyOf')
    one_of: list[Schema] | None = pydantic.Field(None, alias='oneOf')
    not_: Schema | None = pydantic.Field(None, alias='not')
    if_: Schema | None = pydantic.Field(None, alias='if')
    then: Schema | None = None
    else_: Schema | None = pydantic.Field(None, alias='else')

    # Conditional application keywords
    dependent_required: dict[str, list[str]] | None = pydantic.Field(
        None, alias='dependentRequired'
    )
    dependent_schemas: dict[str, Schema] | None = pydantic.Field(
        None, alias='dependentSchemas'
    )

    # Reference keywords
    ref: str | None = pydantic.Field(None, alias='$ref')
    defs: dict[str, Schema] | None = pydantic.Field(None, alias='$defs')

    # Content keywords
    content_media_type: str | None = pydantic.Field(
        None, alias='contentMediaType'
    )
    content_encoding: str | None = pydantic.Field(
        None, alias='contentEncoding'
    )
    content_schema: Schema | None = pydantic.Field(None, alias='contentSchema')

    # Vocabulary-specific keywords
    anchor: str | None = pydantic.Field(None, alias='$anchor')
    dynamic_anchor: str | None = pydantic.Field(None, alias='$dynamicAnchor')
    dynamic_ref: str | None = pydantic.Field(None, alias='$dynamicRef')
    vocabulary: dict[str, bool] | None = pydantic.Field(
        None, alias='$vocabulary'
    )

    # Additional properties for extensibility
    extra: dict[str, typing.Any] | None = None

    model_config = {'extra': 'allow', 'populate_by_name': True}

    @pydantic.model_validator(mode='after')
    def validate_contains_constraints(self) -> Schema:
        """Validate contains constraints."""
        if self.contains is not None:
            # min_contains validation is now handled by Field(ge=1)
            if (
                self.min_contains is not None
                and self.max_contains is not None
                and self.min_contains > self.max_contains
            ):
                raise ValueError(
                    'minContains cannot be greater than maxContains'
                )
        return self

    def __init__(self, **data):
        """Initialize Schema with support for Python types."""
        # Check for Python type in the input data
        python_type = data.get('type')

        # Convert Python type to SchemaType
        if python_type is not None:
            # Store original Python type in the data to be used by the model
            data['py_type'] = python_type

            # Handle Python types that aren't SchemaType objects
            if not isinstance(python_type, SchemaType | list):
                # Convert to SchemaType for Pydantic validation
                if python_type is str:
                    data['type'] = SchemaType.STRING
                elif python_type is int:
                    data['type'] = SchemaType.INTEGER
                elif python_type is float:
                    data['type'] = SchemaType.NUMBER
                elif python_type is bool:
                    data['type'] = SchemaType.BOOLEAN
                elif python_type in (list, tuple):
                    data['type'] = SchemaType.ARRAY
                elif python_type is dict:
                    data['type'] = SchemaType.OBJECT
                elif python_type is type(None):
                    data['type'] = SchemaType.NULL
            # Handle list of types
            elif isinstance(python_type, list):
                converted_types = []
                for item in python_type:
                    if isinstance(item, SchemaType):
                        converted_types.append(item)
                    elif item is str:
                        converted_types.append(SchemaType.STRING)
                    elif item is int:
                        converted_types.append(SchemaType.INTEGER)
                    elif item is float:
                        converted_types.append(SchemaType.NUMBER)
                    elif item is bool:
                        converted_types.append(SchemaType.BOOLEAN)
                    elif item in (list, tuple):
                        converted_types.append(SchemaType.ARRAY)
                    elif item is dict:
                        converted_types.append(SchemaType.OBJECT)
                    elif item is type(None):
                        converted_types.append(SchemaType.NULL)
                    else:
                        # Leave as is for Pydantic to handle validation error
                        pass
                data['type'] = converted_types

        super().__init__(**data)

    @property
    def type(self) -> SchemaType | list[SchemaType] | None:
        """Get the type value."""
        return self.type_value


# Specialized schema types for specific use cases
class ArraySchema(Schema):
    """Schema specifically for array types."""

    def __init__(self, **data):
        """Initialize with array type."""
        super().__init__(**data)
        self.type_value = SchemaType.ARRAY


class BooleanSchema(Schema):
    """Schema specifically for boolean types."""

    def __init__(self, **data):
        """Initialize with boolean type."""
        super().__init__(**data)
        self.type_value = SchemaType.BOOLEAN


class IntegerSchema(Schema):
    """Schema specifically for integer types."""

    def __init__(self, **data):
        """Initialize with integer type."""
        super().__init__(**data)
        self.type_value = SchemaType.INTEGER


class NullSchema(Schema):
    """Schema specifically for null types."""

    def __init__(self, **data):
        """Initialize with null type."""
        super().__init__(**data)
        self.type_value = SchemaType.NULL


class NumberSchema(Schema):
    """Schema specifically for number types."""

    def __init__(self, **data):
        """Initialize with number type."""
        super().__init__(**data)
        self.type_value = SchemaType.NUMBER


class ObjectSchema(Schema):
    """Schema specifically for object types."""

    def __init__(self, **data):
        """Initialize with object type."""
        super().__init__(**data)
        self.type_value = SchemaType.OBJECT


class StringSchema(Schema):
    """Schema specifically for string types."""

    def __init__(self, **data):
        """Initialize with string type."""
        super().__init__(**data)
        self.type_value = SchemaType.STRING


# Format annotation
class FormatAnnotation(pydantic.BaseModel):
    """Format annotation for string instances."""

    format: FormatType | str


# Content schema
class ContentSchema(pydantic.BaseModel):
    """Content schema for string instances."""

    content_media_type: str = pydantic.Field(alias='contentMediaType')
    content_encoding: str | None = pydantic.Field(
        None, alias='contentEncoding'
    )
    content_schema: Schema | None = pydantic.Field(None, alias='contentSchema')

    model_config = {'populate_by_name': True}


# Specialized string schemas with predefined formats
class EmailSchema(StringSchema):
    """Schema for email strings."""

    def __init__(self, **data):
        """Initialize with email format."""
        super().__init__(**data)
        self.format = FormatType.EMAIL


class IdnEmailSchema(StringSchema):
    """Schema for internationalized email strings."""

    def __init__(self, **data):
        """Initialize with idn-email format."""
        super().__init__(**data)
        self.format = FormatType.IDN_EMAIL


class HostnameSchema(StringSchema):
    """Schema for hostname strings."""

    def __init__(self, **data):
        """Initialize with hostname format."""
        super().__init__(**data)
        self.format = FormatType.HOSTNAME


class IdnHostnameSchema(StringSchema):
    """Schema for internationalized hostname strings."""

    def __init__(self, **data):
        """Initialize with idn-hostname format."""
        super().__init__(**data)
        self.format = FormatType.IDN_HOSTNAME


class IPv4Schema(StringSchema):
    """Schema for IPv4 address strings."""

    def __init__(self, **data):
        """Initialize with ipv4 format."""
        super().__init__(**data)
        self.format = FormatType.IPV4


class IPv6Schema(StringSchema):
    """Schema for IPv6 address strings."""

    def __init__(self, **data):
        """Initialize with ipv6 format."""
        super().__init__(**data)
        self.format = FormatType.IPV6


class URISchema(StringSchema):
    """Schema for URI strings."""

    def __init__(self, **data):
        """Initialize with uri format."""
        super().__init__(**data)
        self.format = FormatType.URI


class URIReferenceSchema(StringSchema):
    """Schema for URI reference strings."""

    def __init__(self, **data):
        """Initialize with uri-reference format."""
        super().__init__(**data)
        self.format = FormatType.URI_REFERENCE


class IRISchema(StringSchema):
    """Schema for IRI strings."""

    def __init__(self, **data):
        """Initialize with iri format."""
        super().__init__(**data)
        self.format = FormatType.IRI


class IRIReferenceSchema(StringSchema):
    """Schema for IRI reference strings."""

    def __init__(self, **data):
        """Initialize with iri-reference format."""
        super().__init__(**data)
        self.format = FormatType.IRI_REFERENCE


class UuidSchema(StringSchema):
    """Schema for UUID strings."""

    def __init__(self, **data):
        """Initialize with uuid format."""
        super().__init__(**data)
        self.format = FormatType.UUID


class URITemplateSchema(StringSchema):
    """Schema for URI template strings."""

    def __init__(self, **data):
        """Initialize with uri-template format."""
        super().__init__(**data)
        self.format = FormatType.URI_TEMPLATE


class JsonPointerSchema(StringSchema):
    """Schema for JSON pointer strings."""

    def __init__(self, **data):
        """Initialize with json-pointer format."""
        super().__init__(**data)
        self.format = FormatType.JSON_POINTER


class RelativeJsonPointerSchema(StringSchema):
    """Schema for relative JSON pointer strings."""

    def __init__(self, **data):
        """Initialize with relative-json-pointer format."""
        super().__init__(**data)
        self.format = FormatType.RELATIVE_JSON_POINTER


class RegexSchema(StringSchema):
    """Schema for regular expression strings."""

    def __init__(self, **data):
        """Initialize with regex format."""
        super().__init__(**data)
        self.format = FormatType.REGEX


class DateTimeSchema(StringSchema):
    """Schema for date-time strings."""

    def __init__(self, **data):
        """Initialize with date-time format."""
        super().__init__(**data)
        self.format = FormatType.DATE_TIME


class DateSchema(StringSchema):
    """Schema for date strings."""

    def __init__(self, **data):
        """Initialize with date format."""
        super().__init__(**data)
        self.format = FormatType.DATE


class TimeSchema(StringSchema):
    """Schema for time strings."""

    def __init__(self, **data):
        """Initialize with time format."""
        super().__init__(**data)
        self.format = FormatType.TIME


class DurationSchema(StringSchema):
    """Schema for duration strings."""

    def __init__(self, **data):
        """Initialize with duration format."""
        super().__init__(**data)
        self.format = FormatType.DURATION


# Reference handling
class Reference(pydantic.BaseModel):
    """JSON Schema reference."""

    ref: str = pydantic.Field(alias='$ref')

    model_config = {'populate_by_name': True}
