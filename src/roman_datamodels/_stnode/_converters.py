"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from asdf.extension import Converter, ManifestExtension
from astropy.time import Time

from ._registry import (
    DEFERRED_NODES_BY_MANIFEST_URI,
    DEFERRED_NODES_BY_TAG,
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    # NODE_CONVERTERS,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
)
from ._stnode import _MANIFESTS, NODE_CLASSES  # type: ignore
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode

__all__ = [
    "NODE_EXTENSIONS",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True

    def select_tag(self, obj, tags, ctx):
        return obj.node.tag

    def from_yaml_tree(self, node, tag, ctx):
        obj = NODE_CLASSES_BY_TAG[tag](node)
        obj._read_tag = tag
        return obj


class TaggedObjectNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    @property
    def tags(self):
        return list(OBJECT_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(OBJECT_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        return dict(obj.node._data)


class TaggedListNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    @property
    def tags(self):
        return list(LIST_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(LIST_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj.node)


class TaggedScalarNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    @property
    def tags(self):
        return list(SCALAR_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(SCALAR_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        obj = obj.node
        node = obj.__class__.__bases__[0](obj)

        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)
        return super().from_yaml_tree(node, tag, ctx)


class _DeferredConverter:
    tags: tuple = tuple()

    @property
    def types(self):
        return NODE_CLASSES

    def select_tag(self, obj, tag, ctx):
        return None

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError()

    def to_yaml_tree(self, obj, tag, ctx):
        return DEFERRED_NODES_BY_TAG[obj.tag](obj)


class _DeferredExtension:
    extension_uri = "asdf://something"
    converters = (_DeferredConverter(),)


def _create_extension(manifest_id: str):
    # TODO can pre-index these
    class CustomTaggedObjectNodeConverter(TaggedObjectNodeConverter):
        types = [a for (a, b) in DEFERRED_NODES_BY_MANIFEST_URI[manifest_id] if issubclass(b, TaggedObjectNode)]  # noqa: RUF012

    class CustomTaggedListNodeConverter(TaggedListNodeConverter):
        types = [a for (a, b) in DEFERRED_NODES_BY_MANIFEST_URI[manifest_id] if issubclass(b, TaggedListNode)]  # noqa: RUF012

    class CustomTaggedScalarNodeConverter(TaggedScalarNodeConverter):
        types = [a for (a, b) in DEFERRED_NODES_BY_MANIFEST_URI[manifest_id] if issubclass(b, TaggedScalarNode)]  # noqa: RUF012

    converters = [
        CustomTaggedObjectNodeConverter(),
        CustomTaggedListNodeConverter(),
        CustomTaggedScalarNodeConverter(),
    ]
    return ManifestExtension.from_uri(manifest_id, converters=converters)


NODE_EXTENSIONS = {"_": _DeferredExtension()} | {manifest["id"]: _create_extension(manifest["id"]) for manifest in _MANIFESTS}
