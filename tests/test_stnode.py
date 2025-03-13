from contextlib import nullcontext

import asdf
import pytest

from roman_datamodels import datamodels, maker_utils, stnode
from roman_datamodels import maker_utils as utils
from roman_datamodels.maker_utils._base import NOFN, NONUM, NOSTR
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy, wraps_hashable

from .conftest import MANIFESTS


@pytest.mark.parametrize("tag_def", [tag_def for manifest in MANIFESTS for tag_def in manifest["tags"]])
def test_tag_has_node_class(tag_def):
    class_name = stnode._factories.class_name_from_tag_uri(tag_def["tag_uri"])
    node_class = getattr(stnode, class_name)

    assert asdf.util.uri_match(node_class._pattern, tag_def["tag_uri"])
    if node_class._default_tag == tag_def["tag_uri"]:
        assert tag_def["description"] in node_class.__doc__
        assert tag_def["tag_uri"] in node_class.__doc__
    else:
        default_tag_version = node_class._default_tag.rsplit("-", maxsplit=1)[1]
        tag_def_version = tag_def["tag_uri"].rsplit("-", maxsplit=1)[1]
        assert asdf.versioning.Version(default_tag_version) > asdf.versioning.Version(tag_def_version)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_node_classes_available_via_stnode(node_class):
    assert issubclass(node_class, stnode.TaggedObjectNode | stnode.TaggedListNode | stnode.TaggedScalarNode)
    assert node_class.__module__ == stnode.__name__
    assert hasattr(stnode, node_class.__name__)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_copy(node_class):
    """Demonstrate nodes can copy themselves, but don't always deepcopy."""
    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    node_copy = node.copy()

    # Assert the copy is shallow:
    assert_node_is_copy(node, node_copy, deepcopy=False)

    # If the node only wraps hashable values, then it should "deepcopy" itself because
    # the immutable values cannot actually be copied. In the case, where there is an
    # unhashable value, then the node should not deepcopy itself.
    with nullcontext() if wraps_hashable(node) else pytest.raises(AssertionError):
        assert_node_is_copy(node, node_copy, deepcopy=True)


@pytest.mark.parametrize("node_class", datamodels.MODEL_REGISTRY.keys())
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_deepcopy_model(node_class):
    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    model = datamodels.MODEL_REGISTRY[node_class](node)
    model_copy = model.copy()

    # There is no assert equal for models, but the data inside is what we care about.
    # this is stored under the _instance attribute. We can assert those instances are
    # deep copies of each other.
    assert_node_is_copy(model._instance, model_copy._instance, deepcopy=True)


def test_wfi_mode():
    """
    The WfiMode class includes special properties that map optical_element
    values to grating or filter.
    """
    node = stnode.WfiMode({"optical_element": "GRISM"})
    assert node.optical_element == "GRISM"
    assert node.grating == "GRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "PRISM"})
    assert node.optical_element == "PRISM"
    assert node.grating == "PRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "F129"})
    assert node.optical_element == "F129"
    assert node.grating is None
    assert node.filter == "F129"
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_serialization(node_class, tmp_path):
    file_path = tmp_path / "test.asdf"

    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    with asdf.AsdfFile() as af:
        af["node"] = node
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert_node_equal(af["node"], node)


def test_info(capsys):
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


def test_schema_info():
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)

    info = af.schema_info("archive_catalog")
    assert info == {
        "wfimode": {
            "detector": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(10)",
                        "destination": ["WFIExposure.detector", "GuideWindow.detector", "WFICommon.detector"],
                    },
                    "WFI18",
                )
            },
            "name": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(5)",
                        "destination": [
                            "WFIExposure.instrument_name",
                            "GuideWindow.instrument_name",
                            "WFICommon.instrument_name",
                        ],
                    },
                    "WFI",
                )
            },
            "optical_element": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(20)",
                        "destination": [
                            "WFIExposure.optical_element",
                            "GuideWindow.optical_element",
                            "WFICommon.optical_element",
                        ],
                    },
                    "GRISM",
                )
            },
        }
    }


# Test that a currently undefined attribute can be assigned using dot notation
# so long as the attribute is defined in the corresponding schema.
def test_node_new_attribute_assignment():
    exp = stnode.Exposure()
    exp.nresultants = 5
    assert exp.nresultants == 5
    # Test patternProperties attribute case
    photmod = utils.mk_wfi_img_photom()
    phottab = photmod.phot_table
    newphottab = {"F062": phottab["F062"]}
    photmod.phot_table = newphottab
    photmod.phot_table.F213 = phottab["F213"]
    with pytest.raises(AttributeError):
        photmod.phot_table.F214 = phottab["F213"]


@pytest.mark.parametrize("model", [mdl for mdl in datamodels.MODEL_REGISTRY.values() if "Ref" not in mdl.__name__])
def test_node_representation(model):
    """
    Regression test for #244.

    The DNode object was lacking the __repr__ method, which is used to return
    the representation of the object. The reported issue was with ``mdl.meta.instrument``,
    so that is directly checked here.
    """
    mdl = maker_utils.mk_datamodel(model)

    if hasattr(mdl, "meta"):
        if isinstance(mdl, datamodels.MosaicModel | datamodels.MosaicSegmentationMapModel | datamodels.MosaicSourceCatalogModel):
            assert repr(mdl.meta.basic) == repr(
                {
                    "time_first_mjd": NONUM,
                    "time_last_mjd": NONUM,
                    "time_mean_mjd": NONUM,
                    "max_exposure_time": NONUM,
                    "mean_exposure_time": NONUM,
                    "visit": NONUM,
                    "segment": NONUM,
                    "pass": NONUM,
                    "program": NONUM,
                    "survey": NOSTR,
                    "optical_element": "F158",
                    "instrument": "WFI",
                    "location_name": NOSTR,
                    "product_type": NOSTR,
                }
            )
            model_types = {
                datamodels.MosaicModel: "MosaicModel",
                datamodels.MosaicSegmentationMapModel: "MosaicSegmentationMapModel",
                datamodels.MosaicSourceCatalogModel: "MosaicSourceCatalogModel",
            }
            assert mdl.meta.model_type == model_types[type(mdl)]
            assert mdl.meta.telescope == "ROMAN"
            assert mdl.meta.filename == NOFN
        elif isinstance(mdl, datamodels.SegmentationMapModel | datamodels.ImageSourceCatalogModel):
            assert mdl.meta.optical_element == "F158"
        else:
            assert repr(mdl.meta.instrument) == repr(
                {
                    "name": "WFI",
                    "detector": "WFI01",
                    "optical_element": "F158",
                }
            )
