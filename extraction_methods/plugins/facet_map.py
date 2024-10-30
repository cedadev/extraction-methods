__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class FacetMapInput(Input):
    """Facet Map input model."""

    term_map: dict = Field(
        default={},
        description="Dictionary of terms to be mapped.",
    )


class FacetMapExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``facet_map``

    Description:
        In some cases, you may wish to map the header attributes to different
        facets. This method takes a map and converts the facet labels into those
        specified.

    Configuration Options:
        - ``term_map``: Dictionary of terms to map.

    Example Configuration:
        .. code-block:: yaml
            - method: facet_map
              inputs:
                term_map:
                  old_key: new_key
                  time_coverage_start: start_time
    """

    input_class = FacetMapInput

    @update_input
    def run(self, body: dict) -> dict:
        for old_key, new_key in self.input.term_map:
            try:
                value = body.pop(old_key)
                body[new_key] = value

            except KeyError:
                pass

        return body
