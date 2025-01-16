__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class BboxInput(Input):
    """BBox input model."""

    west: float | str = Field(
        description="west coordinate.",
    )
    south: float | str = Field(
        description="south coordinate.",
    )
    east: float | str = Field(
        description="east coordinate.",
    )
    north: float | str = Field(
        description="north coordinate.",
    )

    def update_attrs(self, body):
        super().update_attrs(body)
        self.west = float(self.west)
        self.south = float(self.south)
        self.east = float(self.east)
        self.north = float(self.north)


class BboxExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``bbox``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
        - ``west``: ``REQUIRED`` Most westerly coordinate.
        - ``south``: ``REQUIRED`` Most southernly coordinate.
        - ``east``: ``REQUIRED`` Most easterly coordinate.
        - ``north``: ``REQUIRED`` Most northernly coordinate.

    Example Configuration:
        .. code-block:: yaml
            - method: bbox
                inputs:
                west: 0
                south: 0
                east: $east_variable
                north: $north_variable
    """

    input_class = BboxInput

    @update_input
    def run(self, body: dict) -> dict:
        try:
            body["bbox"] = {
                "type": "envelope",
                "coordinates": [
                    [
                        self.input.west,
                        self.input.south,
                    ],
                    [
                        self.input.east,
                        self.input.north,
                    ],
                ],
            }

        except (TypeError, KeyError):
            LOGGER.warning("Unable to convert bbox.", exc_info=True)

        return body
