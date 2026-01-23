# encoding: utf-8
"""
..  _json-file:

JSON File Method
----------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import json
import logging
from collections import defaultdict

# Python imports
from pathlib import Path
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class JsonFileInput(Input):
    """
    Model for JSON File Input.
    """

    path: str = Field(
        description="Path to directory of JSON files or single JSON file.",
    )
    properties: list[KeyOutputKey] = Field(
        description="list of properties to extract.",
    )


class JsonFileExtract(ExtractionMethod):
    """
    Method: ``json_file``

    Description:
        Takes an input list of string to extract from the json file.

    Configuration Options:
    .. list-table::

        - ``path``: Path to directory or single JSON file.
        - ``terms``: List of terms to extract.

    Example configuration:
    .. code-block:: yaml

        - method: json_file
          inputs:
            path: /path/to/file.json
            properties:
              - key: MIP_ERA
                output_key: mip_era
    """

    input_class = JsonFileInput

    def extract_terms(self, path: Path) -> dict[str, Any]:
        """
        Extract terms from JSON file(s) at path.

        :param path: path to file
        :type path: Path

        :return: extracted terms
        :rtype: dict
        """

        try:
            with open(path, "r", encoding="utf-8") as json_file:
                load_out = json.load(json_file)
        except ValueError as error:
            LOGGER.debug("File: %s can't be json loaded: %s", path, error)

        output = {}
        for term in self.input.properties:
            if term.key in load_out:
                output[term.output_key] = load_out[term.key]

        return output

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        path = Path(self.input.path)

        if path.is_dir():
            output: dict[str, Any] = defaultdict(list)
            for child in path.rglob("*.json"):
                for k, v in self.extract_terms(child):
                    if isinstance(v, list):
                        output[k].extend(v)
                    else:
                        output[k].append(v)

        if path.is_file():
            output = {path.name: self.extract_terms(path)}

        return body | output
