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
    Input,
    update_input,
)

LOGGER = logging.getLogger(__name__)


class GeometryToBboxInput(Input):
    """Geometry to bbox input model."""

    geometry: str | dict = Field(
        default="$geometry",
        description="geometry to be converted to bbox.",
    )
    output_key: str = Field(
        default="bbox",
        description="key to output to.",
    )


class GeometryToBboxExtract(ExtractionMethod):
    """
    .. list-table::

    Processor Name: ``geometry_to_bbox``

    Description:
        Accepts a geometry with type and list of coordinates to `RFC 7946,
        section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_ formatted bbox.

    Configuration Options:
        - ``geometry``: ``REQUIRED`` geometry to be converted to bbox.
        - ''output_key'': key to output to.

    Example Configuration:
        .. code-block:: yaml
            - method: geometry_to_bbox
                inputs:
                  geometry:
                    type: point
                    coordinates:
                    - 20
                    - 0
    """

    input_class = GeometryToBboxInput

    def point(self, coordinates: list) -> list:
        """
        Get point bbox
        """
        return [
            coordinates[0],
            coordinates[1],
            coordinates[0],
            coordinates[1],
        ]

    def line(self, coordinates: list) -> list:
        """
        Get line bbox
        """
        bbox = self.point(coordinates[0])

        for coordinate in coordinates[1:]:

            if coordinate[0] < bbox[0]:
                bbox[0] = coordinate[0]

            elif coordinate[0] > bbox[2]:
                bbox[2] = coordinate[0]

            if coordinate[1] < bbox[1]:
                bbox[1] = coordinate[1]

            elif coordinate[1] > bbox[3]:
                bbox[3] = coordinate[1]

        return bbox

    def polygon(self, coordinates: list) -> list:
        """
        Get polygon bbox
        """
        return self.line(coordinates[0][1:])

    def multi(self, coordinate_type: str, coordinates: list) -> list:
        """
        Get polygon bbox
        """

        bboxes = [
            self.get_bbox(coordinate_type.lstrip("Multi"), coordinate) for coordinate in coordinates
        ]
        return [
            min(bbox[0] for bbox in bboxes),
            max(bbox[2] for bbox in bboxes),
            min(bbox[1] for bbox in bboxes),
            max(bbox[3] for bbox in bboxes),
        ]

    def get_bbox(self, coordinate_type: str, coordinates: list) -> list:
        """
        Get bbox from geometry
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

        body[self.input.output_key] = self.get_bbox(
            self.input.geometry["type"], self.input.geometry["coordinates"]
        )

        return body
