import asdf
import pytest

from roman_datamodels._stnode._manifest import MANIFESTS
from roman_datamodels._stnode._nodes import NODE_CLASSES
from roman_datamodels._stnode._schema import _tag_uri_to_schema_uri
from roman_datamodels._stnode._tagged import TaggedObjectNode


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=[node_class for node_class in NODE_CLASSES if issubclass(node_class, TaggedObjectNode)])
def object_node(request):
    return request.param


@pytest.fixture(scope="session")
def object_node_default_uri(object_node):
    return _tag_uri_to_schema_uri(object_node._default_tag)


@pytest.fixture(scope="session")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri)]
