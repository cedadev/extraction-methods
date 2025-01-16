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

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    KeyOutputKey,
    SetEntryPoints,
    update_input,
)
from extraction_methods.core.types import Backend, Input

LOGGER = logging.getLogger(__name__)


class HeaderInput(Input):
    """Header input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    backend: Backend = Field(
        description="Backend and kwargs to run.",
    )
    attributes: list[KeyOutputKey] = Field(
        description="List of attributes to be extracted.",
    )


class HeaderExtract(ExtractionMethod, SetEntryPoints):
    """

    .. list-table::

        * - Processor Name
          - ``header``

    Description:
        Takes a uri string and a list of attributes
        and returns a dictionary of the values extracted from the
        file header.

    Configuration Options:
        - ``attributes``: A list of attributes to match for from the file header
        - ``backend``: Specify which backend
        - ``backend_kwargs``: A dictionary of kwargs for the extractor

    Example configuration:
        .. code-block:: yaml

            - method: header
              inputs:
                backend:
                  name: xarray
                  kwargs:
                    decode_times: False
                attributes:
                  - name: institution
                  - name: sensor
                    key: Sensor
                  - name: platform

    """

    input_class = HeaderInput
    entry_point_group = "extraction_methods.header.backends"

    @update_input
    def run(self, body: dict) -> dict:
        backend_entry_point = self.entry_points.get(self.input.backend.name).load()
        backend = backend_entry_point(**self.input.backend.inputs)
        output = backend._run(body)
        body |= output

        return body
