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
from ._stnode import _MANIFESTS, NODE_CLASSES
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

    # def __init_subclass__(cls, **kwargs) -> None:
    #     """
    #     Automatically create the converter objects.
    #     """
    #     super().__init_subclass__(**kwargs)

    #     if not cls.__name__.startswith("_"):
    #         if cls.__name__ in NODE_CONVERTERS:
    #             raise ValueError(f"Duplicate converter for {cls.__name__}")

    #         NODE_CONVERTERS[cls.__name__] = cls()

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


# Here's what I'm thinking...
# Since asdf supports conversion deferral (by returning None from select_tag) we
# can use this to allow node classes to retain tags on read/write cycles.
# First, we make a "deferral" extension with:
# - no tags (will this make a warning? if so use a deferral tag)
# - no manifest
# - all node types (similar to old extensions)
# - a select_tag that returns None
# - a to_yaml_tree that returns a new type of SomeDeferredClass(instance)
#
# Next we define a SomeDeferredClass for every tag (seems unavoidable)
# Create the ASDF extension for the STNode classes.

# make the defer extension that claims support for all node type and returns a
# _Deferred class


class _DeferredConverter:
    tags = tuple()

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


# register each manifest with specialized converters for the deferred nodes
def _create_extension(manifest_id: str):
    # TODO needs to be specific
    # make converters for this list of deferred things
    # types will be the deferred types, which I need to assign to a specific
    # one of the above converters
    #
    # tags are the list of tags from the manifest (which I think the ManifestExtension filters)
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

# NODE_EXTENSIONS = {
#    manifest["id"]: ManifestExtension.from_uri(manifest["id"], converters=NODE_CONVERTERS.values()) for manifest in _MANIFESTS
# }
