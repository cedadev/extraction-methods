__author__ = "Rhys Evans"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class GeometryLineExtract(ExtractionMethod):
    """

    Processor Name: ``line_geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to line geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - name: line_geometry
          inputs:
          coordinate_keys:
            -
              - lon_1
              - lat_1
            -
              - lon_2
              - lat_2

    """

    def run(self, body: dict, **kwargs):
        try:
            coordinates = []

            for coordinate_key in self.coordinate_keys:
                coordinates.append(
                    [
                        float(body[coordinate_key[0]]),
                        float(body[coordinate_key[1]]),
                    ]
                )

            body["geometry"] = {
                "type": "Line",
                "coordinates": coordinates,
            }

        except KeyError:
            LOGGER.warning("Unable to convert to a line geometry.", exc_info=True)

        return body
