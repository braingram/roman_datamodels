"""
Base class for all RomanDataModels

Note this contains only the methods needed to support all RomanDataModels whether
they can be directly serialized to ASDF (tagged) or not.
"""
from __future__ import annotations

__all__ = ["BaseDataModel"]

import abc
import warnings
from collections.abc import Generator
from contextlib import contextmanager, nullcontext
from datetime import datetime
from enum import Enum
from inspect import isclass
from typing import Any, get_args, get_origin

import numpy as np
from astropy.modeling import models
from astropy.time import Time
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from ._metadata import Archive, Archives
from ._utils import annotation_type, field_name, merge_dicts
from .adaptors import get_adaptor


class BaseDataModel(BaseModel, abc.ABC):
    """
    This is the base class to support all RDM features needed by all Pydantic-based data models used.
        This includes:
            - A model configuration to enable/disable certain pydantic features
            - A method to convert the model to an ASDF tree
            - A method to get the archive metadata for the model
            - A method to create a default instance of the model
            - A method to get a flattened dictionary representation of the model
            - A context manager to pause validation of the model
            - Methods for dict-like access to the model
            - A method to copy the model
    """

    model_config = ConfigDict(
        # model_* is a protected namespace for Pydantic, so we have to remove that protection
        # because Basic.model_type is a field we want to use
        protected_namespaces=(),
        # Store the values from an enum not the enum instance
        use_enum_values=True,
        # Allow the model to be populated by field name even if it is aliased.
        #    this is need because pass is a Python syntax word, but it is used as a field name
        #    in the observation schema.
        populate_by_name=True,
        # Allow extra fields to be added to the model
        extra="allow",
        # Validate values when they are set
        validate_assignment=True,
        revalidate_instances="always",
    )

    _validate_setitem: bool = True

    @abc.abstractproperty
    def schema_uri(cls) -> str:
        ...

    def set_validate_setitem(self, value: bool) -> None:
        """
        Change the setitem validation state of the model
        """
        self._validate_setitem = value

    def to_asdf_tree(self) -> dict[str, Any]:
        """
        Convert to an ASDF tree, stopping at tags
        """

        # Avoid circular import
        from roman_datamodels.core import DataModel

        def recurse_tree(field: Any) -> Any:
            """
            Find the sub-tree for a field
                Note, we do not recurse into tagged models because that will be handled by ASDF
            """
            # Recurse into sub-RomanDataModels that are not TaggedDataModels (so ASDF can tag them)
            if isinstance(field, BaseDataModel) and not isinstance(field, DataModel):
                return field.to_asdf_tree()

            # Recurse into sub-dicts
            if isinstance(field, dict):
                return {key: recurse_tree(value) for key, value in field.items()}

            # Recurse into sub-lists
            if isinstance(field, list):
                return [recurse_tree(value) for value in field]

            # Handle enumerations
            if isinstance(field, Enum):
                return field.value

            # Return field if it has no nested data to be serialized
            return field

        # Convert to a dict using built-in Pydantic tricks
        tree = dict(self)
        # loop over loop over the results and recurse into sub-trees converting
        #    as needed
        for name, field in tree.items():
            tree[name] = recurse_tree(field)

        # Handle the case that we have a conflicting keyword with Python
        return {field_name(name): field for name, field in tree.items()}

    @classmethod
    def get_archive_metadata(cls) -> dict[str, Archive | Archives]:
        """Get the archive data for this model"""

        def get_archive(extra: dict[str, Any]) -> Archive:
            """
            Create an archive object
            """
            return Archive(**({} if extra is None else extra))

        metadata = {}

        # loop over the fields in this model
        for name, field in cls.model_fields.items():
            name = field_name(name)

            # Build archive metadata for this field
            if (archive := get_archive(field.json_schema_extra)).has_info:
                metadata[name] = archive
                continue  # If there is archive metadata, we are done

            # Recurse into sub-models
            field_type = annotation_type(field.annotation)

            # Handle the case of field being a RomanDataModel
            #    Note that we do not add the archive metadata if the model has no archive metadata
            if issubclass(field_type, BaseDataModel) and (archive := field_type.get_archive_metadata()):
                metadata[name] = archive

        return metadata

    @classmethod
    def make_default(cls, *, data: dict[str, Any] | None = None, **kwargs) -> BaseDataModel:
        """
        Create a default instance of this model
            Note all arguments to this method are keyword-only.

        Parameters
        ----------
        data :
            Data in the form of a fully nested dictionary representation of the model, specifying
            the overrides to the default values.
        **kwargs :
            The arguments which can be passed down into the specific default value
            construction logic.
        """

        def special_cases(name: str) -> Any:
            """
            Handle the special cases for fields that cannot be easily handled by
            the general logic.
            """
            # Read pattern is a list of lists of integers which significantly complicates
            # the generalized logic to implement, it is easier to just hard code it
            if name == "read_pattern":
                return [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]]

            # The p_exptype field is a string, but it has to follow a regular expression
            #  so it cannot be the nominal string default
            if name == "p_exptype":
                return "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

            # The coordinate_distortion_transform field is a compound model, but it is not
            #     currently directly specified in the schemas, so we hard code it for now.
            if name == "coordinate_distortion_transform":
                return models.Shift(1) & models.Shift(2)

            # Because of the regression tests, we will set the default value for the catalog name
            if name == "tweakreg_catalog_name":
                return "filename_tweakreg_catalog.asdf"

            return None

        def get_default(field_type: type, **kwargs) -> Any:
            """
            Handle getting the default values for fields
            """

            # Recurse into sub-models
            if issubclass(field_type, BaseDataModel):
                return field_type.make_default(**kwargs)

            # Set default numerical scalars
            if field_type is float or field_type is int:
                return -999999

            # Set default strings
            if field_type is str:
                return "dummy value"

            # Set default booleans
            if field_type is bool:
                return False

            # Choose the first value from an enumeration
            if issubclass(field_type, Enum):
                return next(field_type.__iter__()).value

            return None

        def default_list(field: FieldInfo, **kwargs) -> list:
            """
            Handle default values for lists
            """
            # Loop over the types listed in the annotation to get the default values
            return [get_default(type_, **kwargs) for type_ in get_args(field.annotation)]

        def default_dict(field: FieldInfo, name: str, **kwargs) -> dict:
            """
            Handle default values for dicts
            """
            key_type, value_type = get_args(field.annotation)
            keys = (get_default(key_type, **kwargs),)

            # phot_table is a special case because it follows a regular expression,
            #    currently the generator does not encode this into the Pydantic Model
            #    but it is still checked by ASDF during serialization. So we encode
            #    all the normal expected values here. This will be required even if
            #    the generator is updated to encode the regular expression as it will
            #    not be default strings.
            if name == "phot_table":
                keys = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")

            # Loop over the keys generating a default for each value
            return {key: get_default(value_type, **kwargs) for key in keys}

        # Build a dict of default values
        defaults = {}
        for name, field in cls.model_fields.items():
            name = field_name(name)

            # Check if the field has a default value defined by Pydantic,
            #    if so, use that. That value can technically be set in the
            #    schema via the `default` keyword, but ASDF discourages doing so.
            # The default is set to PydanticUndefined if there is no default
            if field.default is not PydanticUndefined and field.default is not None:
                defaults[name] = field.default
                continue

            # Handle the case of fields that are defined via a PydanticAdaptor
            if (adaptor := get_adaptor(field)) is not None:
                defaults[name] = adaptor.make_default(**kwargs)
                continue

            # Handle the special cases that cannot be easily handled by the general logic
            if (value := special_cases(name)) is not None:
                defaults[name] = value
                continue

            # Handle the list/dict cases
            if isclass(origin := get_origin(field.annotation)):
                if issubclass(origin, dict):
                    defaults[name] = default_dict(field, name, **kwargs)
                    continue

                if issubclass(origin, list):
                    defaults[name] = default_list(field, **kwargs)
                    continue

            # Handle all other cases
            if (value := get_default(annotation_type(field.annotation), **kwargs)) is not None:
                defaults[name] = value
                continue

        # Mix in supplied data with the defaults.
        #    This leverages the Pydantic model_dump() method, which dumps the model
        #    to a nested dictionary. We then merge the supplied data into the defaults
        #    and then pass that dictionary back to the model initializer method.
        return cls(**merge_dicts(cls(**defaults).model_dump(), data or {}))

    def to_flat_dict(self, include_arrays: bool = True) -> dict[str, Any]:
        """
        Get a flattened dictionary representation of the model.

        Parameters
        ----------
        include_arrays :
            If true, arrays are included in the dictionary, otherwise they are skipped.
        """

        def convert_value(value: Any) -> Any:
            """Convert times into strings and leave everything else alone"""
            if isinstance(value, datetime):
                return value.isoformat()

            if isinstance(value, Time):
                return str(value)

            return value

        return {
            f"roman.{name}": convert_value(value)
            for name, value in self.flat_items()
            if include_arrays or not isinstance(value, np.ndarray)
        }

    def flat_items(self, *, flatten_lists: bool = True) -> Generator[tuple[str, Any], None, None]:
        """
        Get a generator of flattened items from the model.

        Parameters
        ----------
        flatten_lists :
            If true, lists are flattened with their index acting as the key.
        """

        def recurse(field: Any, path=None) -> Generator[tuple[str, Any], None, None]:
            if path is None:
                path = []

            # Recurse into sub-RomanDataModels that are not TaggedDataModels (so ASDF can tag them)
            if isinstance(field, BaseDataModel):
                for name, value in field:
                    yield from recurse(value, path + [name])

            # Recurse into sub-dicts
            elif isinstance(field, dict):
                for key, value in field.items():
                    yield from recurse(value, path + [key])

            # Recurse into sub-lists
            elif isinstance(field, list) and flatten_lists:
                for index, value in enumerate(field):
                    yield from recurse(value, path + [index])

            # Handle enumerations
            elif isinstance(field, Enum):
                yield from recurse(field.value, path)

            # Return field if it has no nested data to be serialized
            else:
                yield (".".join(str(name) for name in path), field)

        yield from recurse(self)

    @contextmanager
    def pause_validation(self, *, revalidate_on_exit: bool = True) -> None:
        """
        Context manager to pause validation of the model within the context.

        Parameters
        ----------
        revalidate_on_exit :
            If true, revalidate the model on exit of the context manager. Default is True.
        """
        self.model_config["validate_assignment"] = False
        self.model_config["revalidate_instances"] = "never"

        try:
            yield
        finally:
            self.model_config["validate_assignment"] = True
            self.model_config["revalidate_instances"] = "always"

            if revalidate_on_exit:
                self.model_validate(self)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        # Use a null-context rather than using _validate_setitem as the value for
        # revalidate_on_exit because we do not want to revalidate the entire model
        # during this method as other fields may be set purposefully in an invalid
        # fashion.
        if self._validate_setitem:
            context = nullcontext()
        else:
            warnings.warn(
                "RomanDataModel.__setitem__ is circumventing validation, and does not re-validate the model. "
                "This can lead to an invalid model for serialization. To make sure validation occurs, call "
                ".set_validate_setitem(True) on the model",
                RuntimeWarning,
            )
            context = self.pause_validation(revalidate_on_exit=False)

        with context:
            setattr(self, key, value)

    def __contains__(self, item: str) -> bool:
        return item in self.model_fields or item in self.model_extra

    def copy(self, deepcopy: bool = True) -> BaseDataModel:
        """
        Copy method

        Parameters
        ----------
        deepcopy :
            If true, perform a deep copy, otherwise perform a shallow copy. Default is True.
        """
        return self.model_copy(deep=deepcopy)
