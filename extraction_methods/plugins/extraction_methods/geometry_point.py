__author__ = "Rhys Evans"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class GeometryPointExtract(ExtractionMethod):
    """

    Processor Name: ``point_geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to a point geometry. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - name: point_geometry
          inputs:
          coordinate_keys:
            - lon
            - lat

    """

    def run(self, body: dict, **kwargs):
        try:
            coordinates = [
                float(body[self.coordinate_keys[0]]),
                float(body[self.coordinate_keys[1]]),
            ]

            body["geometry"] = {
                "type": "Point",
                "coordinates": coordinates,
            }

        except KeyError:
            LOGGER.warning("Unable to convert to point geometry.", exc_info=True)

        return body
