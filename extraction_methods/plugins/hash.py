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


# Python imports
import hashlib
import logging

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class HashInput(Input):
    """Hash input model."""

    hash_str: str = Field(
        description="string to be hashed.",
    )
    output_key: str = Field(
        description="key to output to.",
    )


class HashExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``hash``

    Description:
        Hashes input string.

    Configuration Options:
        - ``hash_str``: string to be hashed.
        - ``output_key``: key to output to.

    Example configuration:
        .. code-block:: yaml
          id:
            method: hash
            inputs:
              hash_str: $model
              output_key: hashed_terms
    """

    input_class = HashInput

    @update_input
    def run(self, body: dict) -> dict:
        body[self.input.output_key] = hashlib.md5(self.input.input_term.encode("utf-8")).hexdigest()

        return body
