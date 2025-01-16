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
import logging
import re

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RegexInput(Input):
    """Regex input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    regex: str = Field(
        description="The regular expression to match against.",
    )


class RegexExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``regex``

    Description:
        Takes an input string and a regex with
        named capture groups and returns a dictionary of the values
        extracted using the named capture groups.

    Configuration Options:
        - ``input_term``: Term for regex to be ran on.
        - ``regex``: ``REQUIRED`` The regular expression to match against.

    Example configuration:
        .. code-block:: yaml
            - method: regex
              inputs:
                regex: ^(?:[^_]*_){2}(?P<datetime>\d*)

    # noqa: W605
    """

    input_class = RegexInput

    @update_input
    def run(self, body: dict) -> dict:
        result = re.search(rf"{self.input.regex}", self.input.input_term)


        if result:
            body |= result.groupdict()

        else:
            LOGGER.debug("No matches found for regex extract")

        return body
