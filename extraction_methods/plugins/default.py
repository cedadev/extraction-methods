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

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class DefaultInput(Input):
    """Default input model."""

    defaults: dict = Field(
        description="Defaults to be added.",
    )


class DefaultExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``default``

    Description:
        Takes a set of default facets.

    Configuration Options:
        - ``defaults``: Dictionary of defaults to be added.

    Example configuration:
        .. code-block:: yaml
            - method: default
              inputs:
                defaults:
                  mip_era: CMIP6
    """

    input_class = DefaultInput

    @update_input
    def run(self, body: dict) -> dict:
        return body | self.input.defaults
