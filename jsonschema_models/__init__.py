from importlib import metadata

try:
    version = metadata.version('jsonschema-models')
except metadata.PackageNotFoundError:  # pragma: nocover
    version = '0.0.0.dev0'  # Default development version
