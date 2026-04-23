"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from asdf.extension import Converter
from astropy.time import Time

from ._nodes import NODE_CLASSES
from ._registry import (
    MANIFEST_TAG_REGISTRY,
    NODE_CLASSES_BY_TAG,
    TAG_MANIFEST_REGISTRY,
)
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode

if TYPE_CHECKING:
    from ._tagged import SerializationNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

__all__ = [
    "TaggedNodeConverter",
]


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True


class SerializationNodeConverter(_RomanConverter):
    """
    Converter that tags are deferred to so that the correct
    extension can be applied
    """

    def __init__(self, manifest_uri: str, serialization_node):
        self._manifest_uri = manifest_uri
        self._serialization_node = serialization_node

    def select_tag(self, obj: SerializationNode, tags, ctx) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(MANIFEST_TAG_REGISTRY[self._manifest_uri])

    @property
    def types(self) -> tuple[type[SerializationNode], ...]:
        return (self._serialization_node,)

    def to_yaml_tree(self, obj: SerializationNode, tag, ctx):
        return obj.data

    def from_yaml_tree(self, node, tag, ctx) -> TaggedObjectNode | TaggedListNode | TaggedScalarNode:
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        # TODO: Add method for setting read_tag with some checks
        obj = NODE_CLASSES_BY_TAG[tag](node)
        obj._read_tag = tag
        return obj


class TaggedNodeConverter(_RomanConverter):
    def __init__(self, serialization_node_by_manifest_uri):
        self._serialization_node_by_manifest_uri = serialization_node_by_manifest_uri

    def select_tag(self, obj, tags, ctx):
        return None

    @property
    def tags(self) -> tuple:
        return ()

    @property
    def types(self):
        return NODE_CLASSES

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")

    def to_yaml_tree(self, obj, tag, ctx):
        # this is a dispatch node -> 1 of many serialization nodes
        serialization_node = self._serialization_node_by_manifest_uri[TAG_MANIFEST_REGISTRY[obj.tag]]
        if isinstance(obj, TaggedObjectNode):
            data = dict(obj._data)
        elif isinstance(obj, TaggedListNode):
            data = list(obj)
        else:
            if "file_date" in obj.tag:
                converter = ctx.extension_manager.get_converter_for_type(Time)
                data = converter.to_yaml_tree(obj, obj.tag, ctx)
            else:
                data = str(obj)

        return serialization_node(data, obj.tag)
