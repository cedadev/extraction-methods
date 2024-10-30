__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from typing import Literal

from pydantic import Field

# Package imports
from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class GeometryInput(Input):
    """Geometry input model."""

    type: Literal[
        "Point",
        "LineString",
        "Polygon",
        "MultiPointString",
        "MultiLineString",
        "MultiPolygon",
    ] = Field(
        description="Type of geometry to be produced.",
    )
    coordinates: list = Field(
        description="list of coordinates to convert to geometry. Ordering is respected.",
    )
    output_key: str = Field(
        default="geometry",
        description="key to output to.",
    )


class GeometryExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``type``: ``REQUIRED`` Type of geometry to be produced.
        - ``coordinates``: ``REQUIRED`` list of coordinates to convert to geometry. Ordering is respected.
        - ``output_key``: key to output to.

    Example Configuration:
        .. code-block:: yaml
            - name: geometry
            inputs:
                type: line
                coordinates:
                    -
                      - 0
                      - 0
                    -
                      - $lon_2
                      - $lat_2
    """

    input_class = GeometryInput

    def point(self, coordinates: list) -> list:
        """
        Get point coordinates
        """
        return [
            float(coordinates[0]),
            float(coordinates[1]),
        ]

    def line(self, coordinates: list) -> list:
        """
        Get line coordinates
        """
        return [
            [
                float(coordinate[0]),
                float(coordinate[1]),
            ]
            for coordinate in coordinates
        ]

    def polygon(self, coordinates: list) -> list:
        """
        Get polygon coordinates
        """
        coordinates = self.line(coordinates)

        if coordinates[0] != coordinates[-1]:
            # Add the first point to the end to complete the shape
            coordinates.append(coordinates[0])

        return coordinates

    def multi(self, coordinate_type: str, coordinates: list) -> list:
        """
        Get polygon coordinates
        """
        return [
            self.get_coordinates(coordinate_type.lstrip("Multi"), coordinate)
            for coordinate in coordinates
        ]

    def get_coordinates(self, coordinate_type: str, coordinates: list) -> list:
        """
        Get coordinates
        """
        if coordinate_type == "Point":
            return self.point(coordinates)

        if coordinate_type == "Line":
            return self.line(coordinates)

        if coordinate_type == "Polygon":
            return self.polygon(coordinates)

        if coordinate_type.startswith("Multi"):
            return self.multi(coordinate_type, coordinates)

    @update_input
    def run(self, body: dict) -> dict:
        try:
            body[self.input.output_key] = {
                "type": self.input.type,
                "coordinates": self.get_coordinates(
                    self.input.type,
                    self.input.coordinates,
                ),
            }

        except KeyError:
            LOGGER.warning(
                "Unable to convert to a line geometry.",
                exc_info=True,
            )

        return body
