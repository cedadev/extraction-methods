__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import re

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class RemoveInput(Input):
    """Remove input model."""

    keys: list[str] = Field(
        description="list of keys to remove.",
    )
    delimiter: str = Field(
        default=".",
        description="delimiter for nested term.",
    )


class RemoveExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``remove``

    Description:
        remove keys from body.

    Configuration Options:
        - ``keys``: ``REQUIRED`` list of keys to remove.
        - ``delimiter``: delimiter for nested key.

    Example Configuration:
        .. code-block:: yaml
            - method: remove
            inputs:
              keys:
                - hello
                - world
    """

    input_class = RemoveInput

    def compile(self, key: str) -> str:
        """
        Compile key into regex
        """
        key = f"{'^' if key[0] != '^' else ''}{key}{'$' if key[-1] != '$' else ''}"
        return re.compile(key)

    def find_keys(self, keys: list, key_regex: str) -> list:
        """
        Find all keys that match regex
        """
        regex = self.compile(key_regex)

        return list(filter(regex.match, keys))

    def remove_term(self, body: dict, key_parts: list) -> dict:
        """
        Remove nested terms
        """
        if isinstance(body, dict):
            for key_part in key_parts:
                for key in self.find_keys(body.keys(), key_part):
                    if len(key_parts) > 1:
                        body[key] = self.remove_term(body[key], key_parts[1:])

                    else:
                        del body[key]

        return body

    @update_input
    def run(self, body: dict) -> dict:
        for key in self.input.keys:
            key_parts = key.split(self.input.delimiter)
            body = self.remove_term(body, key_parts)

        return body
