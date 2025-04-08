# jsonschema-models

Pydantic models for representing JSON Schema objects.

## Features

- Data model for JSON Schema Draft 2020-12 specification
- Python 3.12+ type annotations
- Pydantic-based models for validation and serialization
- Specialized schema classes for different types (string, number, array, object, etc.)
- Support for references and nested schemas
- Type fields can use Python types (str, int, float, bool, list, dict) or SchemaType enums
- Sypport for specifying format validation:
  - Email formats (email, idn-email)
  - Hostname formats (hostname, idn-hostname)
  - IP address formats (ipv4, ipv6)
  - Resource identifier formats (uri, uri-reference, iri, iri-reference, uuid)
  - Date and time formats (date-time, date, time, duration)
  - URI templates (uri-template)
  - JSON pointers (json-pointer, relative-json-pointer)
  - Regular expressions (regex)

_Note: Currently this library does not enforce the many validation expectations that the 2020-12 specification calls for, it only allows you to implement the shape of the data._

## Installation

```bash
pip install jsonschema-models
```

## Usage

### Basic Usage

```python
import jsonschema_models as jsm

# Create a simple schema
schema = jsm.Schema(
    title='Person',
    type=jsm.SchemaType.OBJECT,  # Or use Python type: type=dict
    properties={
        'name': jsm.Schema(type=jsm.SchemaType.STRING),  # Or use Python type: type=str
        'age': jsm.Schema(type=jsm.SchemaType.INTEGER, minimum=0)  # Or use Python type: type=int
    },
    required=['name']
)

# Convert to JSON Schema
json_schema = schema.model_dump(by_alias=True)
```

### Using Specialized Schema Classes

```python
import jsonschema_models as jsm

# Create a schema using specialized classes
schema = jsm.ObjectSchema(
    title='Person',
    properties={
        'name': jsm.StringSchema(min_length=1),
        'age': jsm.IntegerSchema(minimum=0),
        'hobbies': jsm.ArraySchema(items=jsm.StringSchema()),
        'email': jsm.EmailSchema(description="Contact email"),
        'website': jsm.URISchema(pattern="^https://")
    },
    required=['name', 'email']
)
```

### Working with Format Validation

```python
import jsonschema_models as jsm

# Using format validation with specialized schemas
user_schema = jsm.ObjectSchema(
    title='User',
    properties={
        'id': jsm.UuidSchema(),
        'email': jsm.EmailSchema(min_length=5),
        'website': jsm.URISchema(),
        'registration_date': jsm.DateTimeSchema(),
        'server_hostname': jsm.HostnameSchema(),
        'server_ip': jsm.IPv4Schema()
    },
    required=['id', 'email']
)

# Using format validation with Schema class
contact_schema = jsm.Schema(
    type=jsm.SchemaType.OBJECT,
    properties={
        'email_alternative': jsm.Schema(
            type=jsm.SchemaType.STRING,
            format=jsm.FormatType.EMAIL
        ),
        'phone': jsm.Schema(
            type=jsm.SchemaType.STRING,
            pattern=r'^\+[0-9]{1,3}-[0-9]{3,14}$'
        )
    }
)

# Convert to JSON Schema
json_schema = user_schema.model_dump(by_alias=True)
```

### Working with References

```python
import jsonschema_models as jsm

# Create a schema with references
schema = jsm.Schema(
    title='Root',
    type=dict,
    properties={
        'user': jsm.Schema(ref='#/$defs/user')
    },
    defs={
        'user': jsm.Schema(
            type=dict,
            properties={
                'name': jsm.Schema(type=str),
                'email': jsm.EmailSchema(),
                'created_at': jsm.DateTimeSchema()
            },
            required=['name', 'email']
        )
    }
)
```

## License

BSD License - See LICENSE file for details
