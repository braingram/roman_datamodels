from astropy import time

from roman_datamodels import stnode

from ._base import NOFN, NOSTR


def mk_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the basic-1.0.0 schema)
    """
    meta = {}
    meta["calibration_software_name"] = kwargs.get("calibration_software_name", "RomanCAL")
    meta["calibration_software_version"] = kwargs.get("calibration_software_version", "9.9.0")
    meta["product_type"] = kwargs.get("product_type", "l2")
    meta["filename"] = kwargs.get("filename", NOFN)
    meta["file_date"] = kwargs.get("file_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    meta["model_type"] = kwargs.get("model_type", NOSTR)
    meta["origin"] = kwargs.get("origin", "STSCI/SOC")
    meta["prd_version"] = kwargs.get("prd_version", "8.8.8")
    meta["sdf_software_version"] = kwargs.get("sdf_software_version", "7.7.7")
    meta["telescope"] = kwargs.get("telescope", "ROMAN")

    return meta
