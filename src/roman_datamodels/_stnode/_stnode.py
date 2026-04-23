"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

import asdf

from ._manifest import MANIFESTS
from ._nodes import NODE_CLASSES
from ._registry import (
    NODE_CLASSES_BY_TAG,
)

__all__ = []


# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
for manifest in MANIFESTS:
    manifest_uri = manifest["id"]

    for tag_def in manifest["tags"]:
        tag_uri = tag_def["tag_uri"]

        # populate NODE_CLASSES_BY_TAG FIXME remove this
        for node_class in NODE_CLASSES:
            if not asdf.util.uri_match(node_class._pattern, tag_uri):
                continue
            NODE_CLASSES_BY_TAG[tag_uri] = node_class
