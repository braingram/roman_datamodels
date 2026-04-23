from asdf.extension import ManifestExtension

from ._converters import SerializationNodeConverter


def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    # Importing from ._stnode itself so that all the dynamically created
    #   objects are in fact created
    from . import _stnode  # noqa: F401
    from ._converters import TaggedNodeConverter
    from ._registry import MANIFEST_TAG_REGISTRY

    return [
        ManifestExtension.from_uri(manifest_uri, converters=(SerializationNodeConverter(manifest_uri), TaggedNodeConverter()))
        for manifest_uri in MANIFEST_TAG_REGISTRY
    ]
