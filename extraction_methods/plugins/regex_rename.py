# encoding: utf-8
"""
..  _regex-rename:

Regex Rename Method
-------------------
"""
__author__ = "Rhys Evans"
__date__ = "8 Jul 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


# Python imports
import logging
import re
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RegexOutputKey(Input):
    """
    Model for Regex.
    """

    regex: str = Field(
        description="Regex to test against.",
    )
    output_key: str = Field(
        description="Term for method to output to.",
    )


class RegexRenameInput(Input):
    """
    Model for Regex Rename Input.
    """

    regex_swaps: list[RegexOutputKey] = Field(
        description="Regex and output key combinations.",
    )


class RegexRenameExtract(ExtractionMethod):
    """
    Method: ``regex_rename``

    Description:
        Takes a list of regex and output key combinations. Any existing properties
        that full match a regex are rename to the output key.
        Later regex take precedence.

    Configuration Options:
    .. list-table::

        - ``regex_swaps``: Regex and output key combinations.

    Example configuration:
    .. code-block:: yaml

        - method: regex_rename
          inputs:
            regex_swaps:
              - regex: README
                output_key: metadata

    # noqa: W605
    """

    input_class = RegexRenameInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        output = body.copy()
        for key in body.keys():
            for swap in self.input.regex_swaps:
                if re.fullmatch(rf"{swap.regex}", key):
                    output[swap.output_key] = body[key]

        return output
