# encoding: utf-8
"""
..  _regexlabel:

Regex Label
-----------
"""
__author__ = "Rhys Evans"
__date__ = "8 Jul 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


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


class RegexCastType(Input):
    """Regex output key model."""

    regex: str = Field(
        description="Regex to test against.",
    )
    cast_type: str = Field(
        description="Python type to cast to.",
    )

class RegexTypeCastInput(Input):
    """Regex rename input model."""
    regex_casts: list[RegexCastType] = Field(
        description="Regex and cast type combinations.",
    )


class RegexTypeCastExtract(ExtractionMethod):
    """

    .. list-table::

    Processor Name: ``regex_type_cast``

    Description:
        Takes a list of regex and cast type combinations. Any existing properties
        that full match a regex are cast to the associated type.

    Configuration Options:
        - ``regex_casts``: Regex and cast type combinations.

    Example configuration:
        .. code-block:: yaml
            - method: regex_type_cast
              inputs:
                regex_casts:
                  - regex: clound_cover
                    cast_type: int

    # noqa: W605
    """

    input_class = RegexTypeCastInput

    @update_input
    def run(self, body: dict) -> dict:

        output = body.copy()
        for key in body.keys():
            for regex_cast in self.regex_casts:
                if re.fullmatch(rf"{regex_cast.regex}", key):
                    cast_type = eval(regex_cast.cast_type)
                    output[key] = cast_type(body[key])

        return output
