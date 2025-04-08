# jsonschema-models

Pydantic models for representing JSON Schema objects.

## Features

- Full support for JSON Schema Draft 2020-12 specification
- Python 3.12+ type annotations
- Pydantic-based models for validation and serialization
- Specialized schema classes for different types (string, number, array, object, etc.)
- Support for references and nested schemas
- Type fields can use Python types (str, int, float, bool, list, dict) or SchemaType enums

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
        'hobbies': jsm.ArraySchema(items=jsm.StringSchema())
    },
    required=['name']
)
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
                'email': jsm.Schema(type=str)
            },
            required=['name', 'email']
        )
    }
)
```

## License

BSD License - See LICENSE file for details
