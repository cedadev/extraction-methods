# encoding: utf-8
"""
Collection of functions which can be used to extract metadata from file headers
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging

import xarray as xr
from pydantic import Field

from extraction_methods.core.extraction_method import (
    Input,
    KeyOutputKeyField,
    SetInput,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class XarrayHeaderInput(Input):
    """Intake backend input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    dataset_kwargs: dict = Field(
        default={},
        description="kwargs to open dataset.",
    )
    namespaces: dict = Field(
        default={"ncml": "http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"},
        description="NcML namespaces.",
    )
    attributes: list[KeyOutputKeyField] = Field(
        default={},
        description="attributes to be extracted.",
    )


class XarrayHeader(SetInput):
    """
    XarrayHeader
    ------

    Backend Name: ``XarrayHeader``

    Description:
        Takes an input string and returns a boolean on whether this
        backend can open that file.
    """

    input_class = XarrayHeaderInput

    @update_input
    def run(self) -> dict:
        """
        Takes a dictionary and list of attributes and extracts the metadata.

        :param body: current extracted properties
        :param attributes: attributes to extract
        :param kwargs: kwargs to send to xarray.open_dataset(). e.g. engine to
        specify different engines to use with grib data.

        :return: Dictionary of extracted attributes
        """
        ds = xr.open_dataset(self.input.input_term, **self.input.dataset_kwargs)

        output = {}
        for attribute in self.input.attributes:

            value = ds.attrs.get(attribute.key)
            if value:
                output[attribute.output_key] = value

        return output
