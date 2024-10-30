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

import cf
from pydantic import Field

from extraction_methods.core.extraction_method import (
    Input,
    NameKeyTerm,
    SetInput,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class CfHeaderInput(Input):
    """Intake backend input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    read_kwargs: dict = Field(
        default={},
        description="kwargs for cf read.",
    )
    attributes: list[NameKeyTerm] = Field(
        default={},
        description="attributes to be extracted.",
    )


class CfHeader(SetInput):
    """
    CfHeader
    ------

    Backend Name: ``Cf``

    Description:
        Takes an input string and returns a boolean on whether this
        backend can open that file.
    """

    input_class = CfHeaderInput

    @update_input
    def run(self, body: dict) -> dict:
        """
        Takes a dictionary and list of attributes and extracts the metadata.

        :param body: current extracted properties

        :return: Dictionary of extracted attributes
        """

        field_list = cf.read(self.input.input_term, **self.input.read_kwargs)

        properties = {}
        for field in field_list:
            properties |= field.properties()
            if field.nc_global_attributes():
                properties["global_attributes"] = field.nc_global_attributes()

        output = {}
        for attribute in self.input.attributes:
            if "global_attributes" in properties and properties["global_attributes"][attribute.key]:
                output[attribute.name] = properties["global_attributes"][attribute.key]
            elif attribute in properties:
                output[attribute.name] = properties[attribute.key]

        return output
