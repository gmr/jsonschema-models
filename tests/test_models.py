"""Tests for the JSON Schema models."""

import json
import unittest

import pydantic

import jsonschema_models as jsm


class TestSchema(unittest.TestCase):
    """Test cases for Schema models."""

    def test_schema_basic(self):
        """Test basic schema creation."""
        schema = jsm.Schema(title='Test Schema', description='A test schema')
        self.assertEqual(schema.title, 'Test Schema')
        self.assertEqual(schema.description, 'A test schema')

    def test_schema_with_type(self):
        """Test schema with type specification."""
        schema = jsm.Schema(type=jsm.SchemaType.STRING)
        self.assertEqual(schema.type, jsm.SchemaType.STRING)

        schema = jsm.Schema(type=[jsm.SchemaType.STRING, jsm.SchemaType.NULL])
        self.assertIn(jsm.SchemaType.STRING, schema.type)
        self.assertIn(jsm.SchemaType.NULL, schema.type)

    def test_schema_with_python_types(self):
        """Test schema with Python type specification."""
        # Test Python type mapping
        schema = jsm.Schema(type=str)
        self.assertEqual(schema.type, jsm.SchemaType.STRING)

        schema = jsm.Schema(type=int)
        self.assertEqual(schema.type, jsm.SchemaType.INTEGER)

        schema = jsm.Schema(type=float)
        self.assertEqual(schema.type, jsm.SchemaType.NUMBER)

        schema = jsm.Schema(type=bool)
        self.assertEqual(schema.type, jsm.SchemaType.BOOLEAN)

        schema = jsm.Schema(type=list)
        self.assertEqual(schema.type, jsm.SchemaType.ARRAY)

        schema = jsm.Schema(type=dict)
        self.assertEqual(schema.type, jsm.SchemaType.OBJECT)

        schema = jsm.Schema(type=type(None))
        self.assertEqual(schema.type, jsm.SchemaType.NULL)

        # Test list of Python types
        schema = jsm.Schema(type=[str, int])
        self.assertIn(jsm.SchemaType.STRING, schema.type)
        self.assertIn(jsm.SchemaType.INTEGER, schema.type)

        # Test mixed list
        schema = jsm.Schema(type=[str, jsm.SchemaType.NULL])
        self.assertIn(jsm.SchemaType.STRING, schema.type)
        self.assertIn(jsm.SchemaType.NULL, schema.type)

    def test_complex_schema_with_python_types(self):
        """Test complex schema using Python types."""
        schema = jsm.Schema(
            title='Person',
            type=dict,
            properties={
                'name': jsm.Schema(type=str),
                'age': jsm.Schema(type=int, minimum=0),
            },
            required=['name'],
        )

        self.assertEqual(schema.title, 'Person')
        self.assertEqual(schema.type, jsm.SchemaType.OBJECT)
        self.assertIn('name', schema.properties)
        self.assertIn('age', schema.properties)
        self.assertEqual(schema.properties['name'].type, jsm.SchemaType.STRING)
        self.assertEqual(schema.properties['age'].type, jsm.SchemaType.INTEGER)
        self.assertEqual(schema.properties['age'].minimum, 0)
        self.assertIn('name', schema.required)

    def test_specialized_schemas(self):
        """Test specialized schema classes."""
        string_schema = jsm.StringSchema(minLength=1, maxLength=100)
        self.assertEqual(string_schema.type, jsm.SchemaType.STRING)
        self.assertEqual(string_schema.min_length, 1)
        self.assertEqual(string_schema.max_length, 100)

        number_schema = jsm.NumberSchema(minimum=0, maximum=10)
        self.assertEqual(number_schema.type, jsm.SchemaType.NUMBER)
        self.assertEqual(number_schema.minimum, 0)
        self.assertEqual(number_schema.maximum, 10)

        array_schema = jsm.ArraySchema(items=jsm.StringSchema(), minItems=1)
        self.assertEqual(array_schema.type, jsm.SchemaType.ARRAY)
        self.assertIsInstance(
            array_schema.items, jsm.StringSchema
        )  # Draft 2020-12: items is a single schema
        self.assertEqual(array_schema.min_items, 1)

        object_schema = jsm.ObjectSchema(
            properties={
                'name': jsm.StringSchema(),
                'age': jsm.IntegerSchema(),
            },
            required=['name'],
        )
        self.assertEqual(object_schema.type, jsm.SchemaType.OBJECT)
        self.assertIn('name', object_schema.properties)
        self.assertIn('age', object_schema.properties)
        self.assertIn('name', object_schema.required)

    def test_schema_validation(self):
        """Test schema validation."""
        # Test field constraints
        with self.assertRaises(pydantic.ValidationError):
            jsm.Schema(multiple_of=-1)  # Will be caught by gt=0 constraint

        with self.assertRaises(pydantic.ValidationError):
            jsm.Schema(min_length=-1)  # Will be caught by ge=0 constraint

        with self.assertRaises(pydantic.ValidationError):
            jsm.Schema(
                min_contains=0, contains=jsm.Schema()
            )  # Will be caught by ge=1 constraint

        # Test model validator for constraints between fields
        with self.assertRaises(ValueError):
            jsm.Schema(
                contains=jsm.Schema(), min_contains=5, max_contains=3
            )  # min > max is invalid

    def test_complex_schema(self):
        """Test a more complex schema."""
        schema = jsm.Schema(
            title='Person',
            type=jsm.SchemaType.OBJECT,
            properties={
                'firstName': jsm.Schema(type=jsm.SchemaType.STRING),
                'lastName': jsm.Schema(type=jsm.SchemaType.STRING),
                'age': jsm.Schema(
                    type=jsm.SchemaType.INTEGER,
                    description='Age in years',
                    minimum=0,
                ),
                'contact': jsm.Schema(
                    type=jsm.SchemaType.OBJECT,
                    properties={
                        'email': jsm.Schema(
                            type=jsm.SchemaType.STRING, format='email'
                        ),
                        'phone': jsm.Schema(type=jsm.SchemaType.STRING),
                    },
                    required=['email'],
                ),
                # Test array items with single schema (2020-12 compliant)
                'tags': jsm.Schema(
                    type=jsm.SchemaType.ARRAY,
                    items=jsm.Schema(type=jsm.SchemaType.STRING),
                ),
            },
            required=['firstName', 'lastName'],
        )

        self.assertEqual(schema.title, 'Person')
        self.assertEqual(schema.type, jsm.SchemaType.OBJECT)
        self.assertIn('firstName', schema.properties)
        self.assertIn('lastName', schema.properties)
        self.assertIn('age', schema.properties)
        self.assertIn('contact', schema.properties)
        self.assertEqual(
            schema.properties['contact'].properties['email'].format, 'email'
        )
        self.assertIn('email', schema.properties['contact'].required)
        self.assertIn('firstName', schema.required)
        self.assertIn('lastName', schema.required)

        # Verify 2020-12 compliant items (single schema)
        self.assertIn('tags', schema.properties)
        self.assertEqual(schema.properties['tags'].type, jsm.SchemaType.ARRAY)
        self.assertEqual(
            schema.properties['tags'].items.type, jsm.SchemaType.STRING
        )

    def test_json_schema_serialization(self):
        """Test serialization to JSON Schema."""
        schema = jsm.ObjectSchema(
            title='Person',
            properties={
                'firstName': jsm.StringSchema(),
                'lastName': jsm.StringSchema(),
                'age': jsm.IntegerSchema(minimum=0),
                'hobbies': jsm.ArraySchema(
                    items=jsm.StringSchema()
                ),  # Draft 2020-12: single schema
            },
            required=['firstName', 'lastName'],
        )

        # Convert to dict and then to JSON
        schema_dict = schema.model_dump(by_alias=True)
        schema_json = json.dumps(schema_dict)

        # Parse the JSON back to a dict
        parsed_dict = json.loads(schema_json)

        # Verify the serialized schema
        self.assertEqual(parsed_dict['title'], 'Person')
        self.assertEqual(parsed_dict['type'], 'object')
        self.assertIn('firstName', parsed_dict['properties'])
        self.assertIn('lastName', parsed_dict['properties'])
        self.assertIn('age', parsed_dict['properties'])
        self.assertEqual(parsed_dict['properties']['age']['minimum'], 0)
        self.assertEqual(parsed_dict['properties']['hobbies']['type'], 'array')
        self.assertEqual(parsed_dict['required'], ['firstName', 'lastName'])

    def test_direct_imports(self):
        """Test imports directly from package."""
        # This ensures imports from the package root work correctly
        import jsonschema_models as jsm

        # Create a schema using direct import
        schema = jsm.Schema(title='Test Direct Import')
        self.assertEqual(schema.title, 'Test Direct Import')

        # Create specialized schemas
        string_schema = jsm.StringSchema(minLength=1)
        self.assertEqual(string_schema.type, jsm.SchemaType.STRING)
        self.assertEqual(string_schema.min_length, 1)

    def test_schema_with_references(self):
        """Test schema with references."""
        schema = jsm.Schema(
            title='Root',
            type=jsm.SchemaType.OBJECT,
            properties={'user': jsm.Schema(ref='#/$defs/user')},
            defs={
                'user': jsm.Schema(
                    type=jsm.SchemaType.OBJECT,
                    properties={
                        'name': jsm.Schema(type=jsm.SchemaType.STRING),
                        'email': jsm.Schema(type=jsm.SchemaType.STRING),
                    },
                    required=['name', 'email'],
                )
            },
        )

        self.assertEqual(schema.title, 'Root')
        self.assertEqual(schema.properties['user'].ref, '#/$defs/user')
        self.assertIn('user', schema.defs)
        self.assertEqual(schema.defs['user'].type, jsm.SchemaType.OBJECT)
        self.assertIn('name', schema.defs['user'].properties)
        self.assertIn('email', schema.defs['user'].properties)

    def test_draft_2020_12_features(self):
        """Test 2020-12 specific features like vocabulary and dynamic refs."""
        # Test vocabulary support
        schema = jsm.Schema(
            schema_='https://json-schema.org/draft/2020-12/schema',
            vocabulary={
                'https://json-schema.org/draft/2020-12/vocab/core': True,
                'https://json-schema.org/draft/2020-12/vocab/validation': True,
                'https://json-schema.org/draft/2020-12/vocab/applicator': True,
            },
        )

        self.assertEqual(
            schema.schema_, 'https://json-schema.org/draft/2020-12/schema'
        )
        self.assertIn(
            'https://json-schema.org/draft/2020-12/vocab/core',
            schema.vocabulary,
        )

        # Test dynamic references and anchors
        schema = jsm.Schema(
            type=jsm.SchemaType.OBJECT,
            properties={'pet': jsm.Schema(dynamic_ref='#pet')},
            defs={
                'dog': jsm.Schema(
                    type=jsm.SchemaType.OBJECT,
                    properties={
                        'name': jsm.Schema(type=jsm.SchemaType.STRING),
                        'breed': jsm.Schema(type=jsm.SchemaType.STRING),
                    },
                    anchor='pet',
                ),
                'cat': jsm.Schema(
                    type=jsm.SchemaType.OBJECT,
                    properties={
                        'name': jsm.Schema(type=jsm.SchemaType.STRING),
                        'color': jsm.Schema(type=jsm.SchemaType.STRING),
                    },
                    dynamic_anchor='pet',
                ),
            },
        )

        self.assertEqual(schema.properties['pet'].dynamic_ref, '#pet')
        self.assertEqual(schema.defs['dog'].anchor, 'pet')
        self.assertEqual(schema.defs['cat'].dynamic_anchor, 'pet')

        # Test with deprecated additionalItems
        schema = jsm.Schema(
            type=jsm.SchemaType.ARRAY,
            items=jsm.Schema(type=jsm.SchemaType.STRING),
            additional_items=jsm.Schema(type=jsm.SchemaType.NUMBER),
        )

        self.assertEqual(schema.items.type, jsm.SchemaType.STRING)
        self.assertEqual(schema.additional_items.type, jsm.SchemaType.NUMBER)
