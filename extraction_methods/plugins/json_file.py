# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import json
import logging
import os

# Python imports
from pathlib import Path

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class JsonFileInput(Input):
    """JSON input model."""

    path: str = Field(
        description="Path to directory of JSON files or single JSON file.",
    )
    properties: list[KeyOutputKey] = Field(
        description="list of properties to extract.",
    )


class JsonFileExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``json``

    Description:
        Takes an input list of string to extract from the json file.

    Configuration Options:
        - ``path``: Path to directory or single JSON file.
        - ``terms``: List of terms to extract.

    Example configuration:
        .. code-block:: yaml
            - method: json
              inputs:
                path: /path/to/file.json
                properties:
                  - key: MIP_ERA
                    output_key: mip_era
    """

    input_class = JsonFileInput

    def extract_terms(self, path: Path) -> dict:
        """Extract terms from JSON file(s) at path."""
        try:
            load_out = json.load(path)
        except ValueError as error:
            LOGGER.debug("File: %s can't be json loaded: %s", path, error)

        output = {}
        for term in self.input.properties:
            if term.key in load_out:
                output[term.output_key] = load_out[term.key]

        return output

    def find_and_extract(self) -> dict:
        """Find and extract from JSON files."""
        path = Path(self.input.path)
        output = {}

        if path.is_dir():
            for child in path.iterdir():
                output |= self.extract_terms(child)

        if path.is_file():
            return {path.name: self.extract_terms(path)}

    @update_input
    def run(self, body: dict) -> dict:
        body |= self.find_and_extract()

        return body
