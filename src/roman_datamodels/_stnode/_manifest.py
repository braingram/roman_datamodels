import importlib.resources
from pathlib import Path

import yaml
from rad import resources

__all__ = ["MANIFESTS", "MANIFEST_TAG_REGISTRY", "TAG_MANIFEST_REGISTRY"]


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
# TODO: We should make this use semantic versioning to sort to ensure we don't get something strange
_DATAMODEL_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")], reverse=True)
MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _DATAMODEL_MANIFEST_PATHS]

MANIFEST_TAG_REGISTRY = {}
TAG_MANIFEST_REGISTRY = {}

# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
for manifest in MANIFESTS:
    manifest_uri = manifest["id"]

    MANIFEST_TAG_REGISTRY[manifest_uri] = []
    for tag_def in manifest["tags"]:
        tag_uri = tag_def["tag_uri"]

        # Make serialization intermediate
        if tag_uri not in TAG_MANIFEST_REGISTRY:
            TAG_MANIFEST_REGISTRY[tag_uri] = manifest_uri
            MANIFEST_TAG_REGISTRY[manifest_uri].append(tag_uri)
