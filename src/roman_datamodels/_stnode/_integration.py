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
    from ._converters import TaggedNodeConverter
    from ._manifest import MANIFEST_TAG_REGISTRY
    from ._tagged import SerializationNode

    manifest_uris = list(MANIFEST_TAG_REGISTRY.keys())

    # first make a serialization node for each manifest
    serialization_node_by_manifest_uri = {}
    extensions = []
    for manifest_uri in manifest_uris:
        serialization_node = SerializationNode._factory(manifest_uri)

        # record these in a dict of uri, node
        serialization_node_by_manifest_uri[manifest_uri] = serialization_node

        # give each taggednodeconverter the mapping
        extensions.append(
            ManifestExtension.from_uri(
                manifest_uri,
                converters=(
                    SerializationNodeConverter(manifest_uri, serialization_node),
                    TaggedNodeConverter(serialization_node_by_manifest_uri),
                ),
            )
        )
    return extensions
