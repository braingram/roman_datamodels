"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Generic, TypeVar

from ._manifest import TAG_MANIFEST_REGISTRY
from ._node import DNode, LNode
from ._schema import _NO_VALUE, Builder, FakeDataBuilder, NodeBuilder, _get_node_class_for_tag, _get_schema_from_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from typing import Any, ClassVar, Self, TypeAlias

    from ._node import _NodeMixin as NodeMixin
else:
    NodeMixin: TypeAlias = object

__all__ = ["SerializationNode", "TaggedListNode", "TaggedObjectNode", "TaggedScalarNode"]


class _DefaultTagClassProperty:
    """
    This is a stop-gap for romancal usage of _default_tag.
    Once new API is added and romancal updated this can be removed.
    """

    def __get__(self, obj, objtype=None):
        # return latest tag for this class TODO pre-compute this
        tags = []
        for tag in TAG_MANIFEST_REGISTRY:
            node_class = _get_node_class_for_tag(tag)
            if node_class is objtype:
                tags.append(tag)
        return sorted(tags)[-1]


class _TaggedNodeMixin(NodeMixin):
    """
    Mixin class to provide the common API for all tagged objects.

    Note: the _create_* methods are prefixed with an underscore to prevent them from
        exposing the builder parameter to as part of the public API. They are the real
        implementations of the public create_* methods, which simply call the underscored
        versions without passing a builder. The builder is argument is needed by the Builder
        objects to pass themselves back through the chain of building calls during nested
        building operations.
    """

    __slots__ = ()

    _pattern: ClassVar[str]

    _default_tag = _DefaultTagClassProperty()

    @classmethod
    def _create_minimal(
        cls, defaults: Mapping[str, Any] | None = None, builder: Builder | None = None, *, tag: str | None = None
    ) -> Self:
        builder = builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def create_minimal(cls, defaults: Mapping[str, Any] | None = None, *, tag: str | None = None) -> Self:
        """
        Create a minimal instance of this class, only things with the attributes
        which have a default value that can be determined.

        Parameters
        ----------
        defaults : Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        tag : str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """
        return cls._create_minimal(defaults, tag=tag)

    @classmethod
    def _create_fake_data(
        cls,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        *,
        tag: str | None = None,
    ) -> Self:
        return cls._create_minimal(defaults, builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_fake_data(
        cls, defaults: Mapping[str, Any] | None = None, shape: tuple[int, ...] | None = None, *, tag: str | None = None
    ) -> Self:
        """
        Create an instance of this class with with all required attributes
        filled in with fake data.

        Parameters
        ----------
        defaults: Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        shape: tuple[int, ...] | None
            The shape of the data to create
        tag: str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """
        return cls._create_fake_data(defaults, shape, tag=tag)

    @classmethod
    def _create_from_node(cls, node: MutableMapping[str, Any], builder: Builder | None = None, *, tag: str | None = None) -> Self:
        return cls._create_minimal(node, builder or NodeBuilder(), tag=tag)

    @classmethod
    def create_from_node(cls, node: MutableMapping[str, Any], *, tag: str | None = None) -> Self:
        """
        Create an instance of this class from a node (dict-like object)

        Parameters
        ----------
        node: MutableMapping[str, Any]
            The node to create the instance from
        tag: str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """
        return cls._create_from_node(node, tag=tag)

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return _get_schema_from_tag(self.tag)


class TaggedObjectNode(DNode, _TaggedNodeMixin):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()


class TaggedListNode(LNode, _TaggedNodeMixin):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()


class TaggedScalarNode(_TaggedNodeMixin):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def __asdf_traverse__(self):
        return self

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag: str | None = None):
        builder = builder or Builder()
        value = builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults)
        if value is _NO_VALUE:
            return value

        new = cls(value)
        if tag:
            new._read_tag = tag

        return new

    @property
    def _tag(self):
        # _tag is required by asdf to allow __asdf_traverse__
        return getattr(self, "_read_tag", self._default_tag)

    def copy(self):
        return copy.copy(self)


_T = TypeVar("_T", bound=TaggedObjectNode | TaggedListNode | TaggedScalarNode)


class SerializationNode(Generic[_T]):
    """
    Intermediate class used to assist in serialization of Tagged objects
    so that the extension is correctly written.
    """

    _manifest: ClassVar[str]

    def __init__(self, data: _T, tag: str):
        self._data = data
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def data(self) -> _T:
        return self._data

    @classmethod
    def _factory(cls, manifest: str) -> type[SerializationNode]:
        """Create a subclass of this for the given tag"""
        _, version = manifest.rsplit("-", maxsplit=1)

        return type(
            f"SerializationNode__{version.replace('.', '_')}",
            (SerializationNode,),
            {
                "_manifest": manifest,
                "__module__": "roman_datamodels._stnode",
            },
        )


tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]
