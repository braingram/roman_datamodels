import asdf
import pytest

from roman_datamodels._stnode._registry import OBJECT_NODE_CLASSES_BY_PATTERN
from roman_datamodels._stnode._schema import _tag_uri_to_schema_uri
from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=list(OBJECT_NODE_CLASSES_BY_PATTERN.values()))
def object_node(request):
    return request.param


@pytest.fixture(scope="session")
def object_node_default_uri(object_node):
    return _tag_uri_to_schema_uri(object_node._default_tag)


@pytest.fixture(scope="session")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri)]
