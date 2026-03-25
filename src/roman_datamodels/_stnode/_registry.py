"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._converters import _RomanConverter
    from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, _DeferredNode, tagged_type

OBJECT_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedObjectNode]] = {}
LIST_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedListNode]] = {}
SCALAR_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedScalarNode]] = {}
NODE_CONVERTERS: dict[str, type[_RomanConverter]] = {}
NODE_CLASSES_BY_TAG: dict[str, tagged_type] = {}
SCHEMA_URIS_BY_TAG: dict[str, str] = {}
DEFERRED_NODES_BY_TAG: dict[str, type[_DeferredNode]] = {}
DEFERRED_NODES_BY_EXTENSION_URI: dict[str, list[type[_DeferredNode]]] = {}
