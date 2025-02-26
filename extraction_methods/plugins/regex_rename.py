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
from collections.abc import KeysView
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
    nest_delimiter: str = Field(
        default="",
        description="delimiter for nested term.",
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

    def matching_keys(self, keys: KeysView[str], key_regex: str) -> list[str]:
        """
        Find all keys that match regex

        :param keys: dictionary keys to test
        :type keys: KeysView
        :param key_regex: regex to test against
        :type key_regex: str

        :return: matching keys
        :rtype: list
        """

        regex = re.compile(key_regex)

        return list(filter(regex.match, keys))

    def rename(
        self, body: dict[str, Any], key_parts: list[str], output_key: str
    ) -> dict[str, Any]:
        """
        Rename terms

        :param body: current body
        :type body: dict
        :param key_parts: key parts seperated by delimiter
        :type key_parts: list

        :return: dict
        :rtype: update body
        """

        for key in self.matching_keys(body.keys(), key_parts[0]):

            if len(key_parts) > 1:
                body[key] = self.rename(body[key], key_parts[1:], output_key)

            else:
                body[output_key] = body[key]
                del body[key]

        return body

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        for swap in self.input.regex_swaps:
            nest = (
                swap.regex.split(self.input.delimiter)
                if self.input.delimiter
                else [swap.regex]
            )

            body = self.rename(body, nest, swap.output_key)

        return body
