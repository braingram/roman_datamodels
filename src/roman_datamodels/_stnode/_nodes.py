import re
from copy import deepcopy
from typing import ClassVar

from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype
from astropy.time import Time

from roman_datamodels._stnode._schema import Builder, _get_keyword, _get_properties, _get_schema_from_tag
from roman_datamodels._stnode._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode


class CalLogs(TaggedListNode):
    """Calibration log message"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/cal_logs-*"
    __slots__ = ()


class CalibrationSoftwareName(str, TaggedScalarNode):
    """Name of the calibration software package used in
    processing this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_name-*"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("RomanCAL")
        if tag:
            new._read_tag = tag

        return new


class CalibrationSoftwareVersion(str, TaggedScalarNode):
    """The version number of the calibration software used in
    processing this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-*"


class ProductType(str, TaggedScalarNode):
    """A descriptor for the type of data contained within the
    file. This corresponds to the standard file suffixes for
    archival data products. Consult the documentation for the list
    of options."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/product_type-*"


class Filename(str, TaggedScalarNode):
    """The auto-generated name of this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/filename-*"


class FileDate(Time, TaggedScalarNode):
    """The date and time this file was created."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/file_date-*"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls.now()
        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("2020-01-01T00:00:00.0", format="isot", scale="utc")
        if tag:
            new._read_tag = tag

        return new


class ModelType(str, TaggedScalarNode):
    """The type of data model contained within this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/model_type-*"


class Origin(str, TaggedScalarNode):
    """The name of the institution of organization
    responsible for creating this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/origin-*"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("STSCI/SOC")
        if tag:
            new._read_tag = tag

        return new


class PrdVersion(str, TaggedScalarNode):
    """The version number of the Science Operations Center
    (SOC) Project Reference Database (PRD) used in generating this
    file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/prd_version-*"

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("8.8.8")
        if tag:
            new._read_tag = tag

        return new


class SdfSoftwareVersion(str, TaggedScalarNode):
    """The version number of the Science Operations Center
    (SOC) Science Data Formatting (SDF) software used in generating
    this file."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-*"

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("7.7.7")
        if tag:
            new._read_tag = tag

        return new


class Telescope(str, TaggedScalarNode):
    """The name of the telescope used to acquire the data."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/telescope-*"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("ROMAN")
        if tag:
            new._read_tag = tag

        return new


class FpsCalibrationSoftwareVersion(str, TaggedScalarNode):
    """FPS Calibration software version number"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/calibration_software_version-*"


class FpsFilename(str, TaggedScalarNode):
    """FPS Name of the file"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/filename-*"


class FpsFileDate(FileDate):
    """FPS Date this file was created (UTC)"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-*"


class FpsModelType(str, TaggedScalarNode):
    """FPS Type of data model"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/model_type-*"


class FpsOrigin(str, TaggedScalarNode):
    """FPS Organization responsible for creating file"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/origin-*"


class FpsPrdSoftwareVersion(str, TaggedScalarNode):
    """FPS S&OC PRD version number used in data processing"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/prd_software_version-*"


class FpsSdfSoftwareVersion(str, TaggedScalarNode):
    """FPS SDF software version number"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/sdf_software_version-*"


class FpsTelescope(str, TaggedScalarNode):
    """FPS Telescope used to acquire the data"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/telescope-*"


class TvacCalibrationSoftwareVersion(str, TaggedScalarNode):
    """TVAC Calibration software version number"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/calibration_software_version-*"


class TvacFilename(str, TaggedScalarNode):
    """TVAC Name of the file"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/filename-*"


class TvacFileDate(FileDate):
    """TVAC Date this file was created (UTC)"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-*"


class TvacModelType(str, TaggedScalarNode):
    """TVAC Type of data model"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/model_type-*"


class TvacOrigin(str, TaggedScalarNode):
    """TVAC Organization responsible for creating file"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/origin-*"


class TvacPrdSoftwareVersion(str, TaggedScalarNode):
    """TVAC S&OC PRD version number used in data processing"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/prd_software_version-*"


class TvacSdfSoftwareVersion(str, TaggedScalarNode):
    """TVAC SDF software version number"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/sdf_software_version-*"


class TvacTelescope(str, TaggedScalarNode):
    """TVAC Telescope used to acquire the data"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/telescope-*"


class L1FaceGuidewindow(TaggedObjectNode):
    """Level 1 FACE Guide Star Window Information schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/l1_face_guidewindow-*"
    __slots__ = ()


class L1DetectorGuidewindow(TaggedObjectNode):
    """Level 1 Detector Guide Star Window Information schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/l1_detector_guidewindow-*"
    __slots__ = ()


class Ramp(TaggedObjectNode):
    """Ramp schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/ramp-*"
    __slots__ = ()


class WfiScienceRaw(TaggedObjectNode):
    """Basic Roman Raw Science"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-*"
    __slots__ = ()


class WfiImage(TaggedObjectNode):
    """Wfi level 2 image information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_image-*"
    __slots__ = ()


class WfiMosaic(TaggedObjectNode):
    """Wfi level 3 mosaic information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-*"
    __slots__ = ()


class WfiWcs(TaggedObjectNode):
    """Roman Wide Field Instrument (WFI) Level 2 (L2) WCS and
    modified WCS applicable for Science Raw (L1)."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_wcs-*"
    __slots__ = ()


class AbvegaoffsetRef(TaggedObjectNode):
    """AB Vega Offset reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/abvegaoffset-*"
    __slots__ = ()


class ApcorrRef(TaggedObjectNode):
    """Aperture correction reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/apcorr-*"
    __slots__ = ()


class DarkRef(TaggedObjectNode):
    """Dark reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-*"
    __slots__ = ()


class DetectorstatusRef(TaggedObjectNode):
    """Reference file that is a summary for the current status of each WFI detector to support prompt processing."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/detectorstatus-*"
    __slots__ = ()


class DarkdecaysignalRef(TaggedObjectNode):
    """Dark decay reference file contains the residual signal properties for each WFI detector
    that can be removed by an exponentially decreasing signal of DN with respect to time."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/darkdecaysignal-*"
    __slots__ = ()


class DistortionRef(TaggedObjectNode):
    """Distortion reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-*"
    __slots__ = ()


class EpsfRef(TaggedObjectNode):
    """ePSF reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/epsf-*"
    __slots__ = ()


class EtcRef(TaggedObjectNode):
    """Exposure Time Calculator Reference File Schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/etc-*"
    __slots__ = ()


class FlatRef(TaggedObjectNode):
    """Flat field information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-*"
    __slots__ = ()


class GainRef(TaggedObjectNode):
    """Gain reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-*"
    __slots__ = ()


class IntegralnonlinearityRef(TaggedObjectNode):
    """Integral nonlinearity correction reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/integralnonlinearity-*"
    __slots__ = ()


class InverselinearityRef(TaggedObjectNode):
    """Inverse linearity correction reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-*"
    __slots__ = ()


class IpcRef(TaggedObjectNode):
    """IPC kernel reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-*"
    __slots__ = ()


class LinearityRef(TaggedObjectNode):
    """Linearity correction reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-*"
    __slots__ = ()


class MaskRef(TaggedObjectNode):
    """DQ Mask reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-*"
    __slots__ = ()


class PixelareaRef(TaggedObjectNode):
    """Pixel area reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-*"
    __slots__ = ()


class ReadnoiseRef(TaggedObjectNode):
    """Read noise reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-*"
    __slots__ = ()


class RefpixRef(TaggedObjectNode):
    """Reference pixel correction reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-*"
    __slots__ = ()


class SaturationRef(TaggedObjectNode):
    """Saturation reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-*"
    __slots__ = ()


class SuperbiasRef(TaggedObjectNode):
    """Super-bias reference schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-*"
    __slots__ = ()


class WfiImgPhotomRef(TaggedObjectNode):
    """WFI imaging photometric flux conversion data model"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-*"
    __slots__ = ()


class SkycellsRef(TaggedObjectNode):
    """This file contains definitions for all the skycells that cover the entire celestial sphere"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/skycells-*"
    __slots__ = ()


class MatableRef(TaggedObjectNode):
    """Multiple Accumulation Table Reference File Schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/matable-*"
    __slots__ = ()


class ImageSourceCatalog(TaggedObjectNode):
    """Photometry and astrometry computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-*"
    __slots__ = ()

    def get_column_definition(self, name):
        """
        Get the definition of a named column in the catalog table.

        This function parses the "definitions" part of the catalog
        schema and returns the parsed content.

        Parameters
        ----------
        name: str
            Column name, may contain aperture radisu or filter/band or prefixed
            with ``forced_``.

        Returns
        -------
        dict or None
            Dictionary containing unit, description, and datatype information
            or None if the name does not match any definition.
        """
        if name.startswith("forced_"):
            _, name = name.split("forced_", maxsplit=1)
        definitions = _get_keyword(self.get_schema()["properties"]["source_catalog"], "definitions")
        for def_name, definition in definitions.items():
            if "~radius~" in def_name:
                def_name = def_name.replace("~radius~", r"[0-9]{2}")
            if "_~band~" in def_name:
                def_name = def_name.replace("_~band~", r"(_f[0-9]{3}|)")
            if "~band~" in def_name:
                def_name = def_name.replace("~band~", r"(f[0-9]{3}|)")
            if re.match(f"^{def_name}$", name):
                return {
                    "unit": definition["unit"],
                    "description": definition["description"],
                    "datatype": asdf_datatype_to_numpy_dtype(
                        definition["properties"]["data"]["properties"]["datatype"]["enum"][0]
                    ),
                }

    @classmethod
    def _create_empty_catalog(cls, tag=None, aperture_radii=None, filters=None):
        from astropy.table import Column, Table

        aperture_radii = aperture_radii or ["00"]
        filters = filters or ["f184"]

        columns_schema = dict(_get_properties(_get_schema_from_tag(tag or cls._default_tag)["properties"]["source_catalog"]))
        columns = []

        if "columns" in columns_schema:
            for raw_col_def in columns_schema["columns"]["allOf"]:
                col_def = raw_col_def["not"]["items"]["not"]
                properties = dict(_get_properties(col_def))
                name_regex = properties["name"]["pattern"]
                unit = _get_keyword(col_def, "unit")
                description = _get_keyword(col_def, "description")
                dtype = asdf_datatype_to_numpy_dtype(properties["data"]["properties"]["datatype"]["enum"][0])

                name_queue = [name_regex[1:-1]]

                substitutions = [
                    (r"\[0-9]\{2}", aperture_radii),
                    (r"\(.*\)", filters),
                ]
                while name_queue:
                    name = name_queue.pop()
                    for regex, values in substitutions:
                        if re.search(regex, name):
                            name_queue.extend(re.sub(regex, value, name) for value in values)
                            break
                    else:
                        columns.append(Column([], unit=unit, description=description, dtype=dtype, name=name))

        return Table(columns)

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        defaults = defaults or {}
        if "source_catalog" not in defaults:
            defaults["source_catalog"] = cls._create_empty_catalog(tag=tag)
        return super()._create_fake_data(defaults, shape, builder, tag=tag)


class SegmentationMap(TaggedObjectNode):
    """Segmentation map computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/segmentation_map-*"
    __slots__ = ()


class MosaicSourceCatalog(ImageSourceCatalog):
    """Photometry and astrometry computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-*"
    __slots__ = ()


class MultibandSourceCatalog(ImageSourceCatalog):
    """Photometry and astrometry computed by the Multiband Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-*"
    __slots__ = ()


class MosaicSegmentationMap(TaggedObjectNode):
    """Segmentation map computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/mosaic_segmentation_map-*"
    __slots__ = ()


class MultibandSegmentationMap(TaggedObjectNode):
    """Segmentation map computed by the Multiband Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/multiband_segmentation_map-*"
    __slots__ = ()


class ForcedImageSourceCatalog(ImageSourceCatalog):
    """Photometry and astrometry computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-*"
    __slots__ = ()


class ForcedMosaicSourceCatalog(ImageSourceCatalog):
    """Photometry and astrometry computed by the Source Catalog Step"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-*"
    __slots__ = ()


class MsosStack(TaggedObjectNode):
    """Level 3 schema for SSC's MSOS stack products"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/msos_stack-*"
    __slots__ = ()


class RampFitOutput(TaggedObjectNode):
    """Ramp fit output schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-*"
    __slots__ = ()


class Guidewindow(TaggedObjectNode):
    """Guide window schema"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/guidewindow-*"
    __slots__ = ()


class WfiMode(TaggedObjectNode):
    """Roman WFI Instrument"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-*"
    __slots__ = ()

    # Every optical element is a grating or a filter
    #   There are less gratings than filters so its easier to list out the
    #   gratings.
    _GRATING_OPTICAL_ELEMENTS: ClassVar = {"GRISM", "PRISM"}

    @property
    def filter(self):
        """
        Returns the filter if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None
        else:
            return self.optical_element

    @property
    def grating(self):
        """
        Returns the grating if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element
        else:
            return None


class Exposure(TaggedObjectNode):
    """Exposure information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/exposure-*"
    __slots__ = ()


class Program(TaggedObjectNode):
    """Program information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/program-*"
    __slots__ = ()


class Observation(TaggedObjectNode):
    """Observation information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/observation-*"
    __slots__ = ()


class Ephemeris(TaggedObjectNode):
    """Ephemeris information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/ephemeris-*"
    __slots__ = ()


class Visit(TaggedObjectNode):
    """Visit information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/visit-*"
    __slots__ = ()


class Photometry(TaggedObjectNode):
    """Photometry information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/photometry-*"
    __slots__ = ()


class SourceCatalog(TaggedObjectNode):
    """Source catalog for TweakReg"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/source_catalog-*"
    __slots__ = ()


class Coordinates(TaggedObjectNode):
    """Coordinate frame information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/coordinates-*"
    __slots__ = ()


class Pointing(TaggedObjectNode):
    """Spacecraft Pointing information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/pointing-*"
    __slots__ = ()


class Rcs(TaggedObjectNode):
    """Relative Calibration System Information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/rcs-*"
    __slots__ = ()


class Statistics(TaggedObjectNode):
    """Basic Statistical Information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/statistics-*"
    __slots__ = ()


class VelocityAberration(TaggedObjectNode):
    """Velocity aberration information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-*"
    __slots__ = ()


class Wcsinfo(TaggedObjectNode):
    """Wcsinfo information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/wcsinfo-*"
    __slots__ = ()


class Guidestar(TaggedObjectNode):
    """Guidestar information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/guidestar-*"
    __slots__ = ()


class L2CalStep(TaggedObjectNode):
    """Level 2 Calibration Step status information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/l2_cal_step-*"
    __slots__ = ()

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        defaults = defaults or {}
        schema = _get_schema_from_tag(tag or cls._default_tag)
        new = cls({k: defaults.get(k, "INCOMPLETE") for k in schema["properties"]})
        if tag:
            new._read_tag = tag

        return new


class OutlierDetection(TaggedObjectNode):
    """Outlier Detection information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/outlier_detection-*"
    __slots__ = ()


class SkyBackground(TaggedObjectNode):
    """Sky Background Information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/sky_background-*"
    __slots__ = ()


class MosaicBasic(TaggedObjectNode):
    """Basic mosaic metadata keywords"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/mosaic_basic-*"
    __slots__ = ()


class Associations(TaggedObjectNode):
    """Association table"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/associations-*"
    __slots__ = ()


class RefFile(TaggedObjectNode):
    """Calibration reference file names."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/ref_file-*"
    __slots__ = ()

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        # copy defaults as we may modify them below
        if defaults:
            defaults = deepcopy(defaults)
        else:
            defaults = {}
        schema = _get_schema_from_tag(tag or cls._default_tag)
        for k, v in schema["properties"].items():
            if v["type"] != "string":
                continue
            if k in defaults:
                continue
            defaults[k] = "N/A"
        if not builder:
            builder = Builder()
        data = builder.from_object(schema, defaults)
        new = cls(data)
        if tag:
            new._read_tag = tag

        return new


class L3CalStep(L2CalStep):
    """Level 3 Calibration Step status information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-*"
    __slots__ = ()


class Resample(TaggedObjectNode):
    """Resample information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/resample-*"
    __slots__ = ()


class IndividualImageMeta(TaggedObjectNode):
    """Combined level 2 metadata"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/individual_image_meta-*"
    __slots__ = ()


class MosaicAssociations(TaggedObjectNode):
    """Mosaic associations metadata keywords"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/mosaic_associations-*"
    __slots__ = ()


class MosaicWcsinfo(TaggedObjectNode):
    """Mosaic WCS parameters"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/mosaic_wcsinfo-*"
    __slots__ = ()


class Fps(TaggedObjectNode):
    """FPS test data"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps-*"
    __slots__ = ()


class FpsCalStep(TaggedObjectNode):
    """FPS Level 2 Calibration Step status information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/cal_step-*"
    __slots__ = ()


class FpsExposure(TaggedObjectNode):
    """FPS Exposure information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/exposure-*"
    __slots__ = ()


class FpsGroundtest(TaggedObjectNode):
    """FPS Ground test description."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/groundtest-*"
    __slots__ = ()


class FpsGuidestar(TaggedObjectNode):
    """FPS Guidestar information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/guidestar-*"
    __slots__ = ()


class FpsStatistics(TaggedObjectNode):
    """FPS Summary Statistics"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/statistics-*"
    __slots__ = ()


class FpsRefFile(TaggedObjectNode):
    """FPS Calibration reference file names."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/ref_file-*"
    __slots__ = ()


class FpsWfiMode(TaggedObjectNode):
    """FPS Roman WFI Instrument"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/fps/wfi_mode-*"
    __slots__ = ()


class Tvac(TaggedObjectNode):
    """TVAC test data"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac-*"
    __slots__ = ()


class TvacCalStep(TaggedObjectNode):
    """TVAC Level 2 Calibration Step status information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/cal_step-*"
    __slots__ = ()


class TvacExposure(TaggedObjectNode):
    """TVAC Exposure information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/exposure-*"
    __slots__ = ()


class TvacGroundtest(TaggedObjectNode):
    """TVAC Ground test description."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/groundtest-*"
    __slots__ = ()


class TvacGuidestar(TaggedObjectNode):
    """TVAC Guidestar information"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/guidestar-*"
    __slots__ = ()


class TvacStatistics(TaggedObjectNode):
    """TVAC Summary Statistics"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/statistics-*"
    __slots__ = ()


class TvacRefFile(TaggedObjectNode):
    """TVAC Calibration reference file names."""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/ref_file-*"
    __slots__ = ()


class TvacWfiMode(TaggedObjectNode):
    """TVAC Roman WFI Instrument"""

    _pattern = "asdf://stsci.edu/datamodels/roman/tags/tvac/wfi_mode-*"
    __slots__ = ()


# FIXME make this less hacky
NODE_CLASSES = [obj for obj in locals().values() if isinstance(obj, type) and obj.__module__ == __loader__.name]
