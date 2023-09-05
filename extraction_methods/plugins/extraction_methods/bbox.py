__author__ = "Rhys Evans"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class BboxExtract(ExtractionMethod):
    """

    Processor Name: ``bbox``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
        - ``coordinate_keys``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.

    Example Configuration:

    .. code-block:: yaml

        - method: bbox
            inputs:
            coordinate_keys:
                - west
                - south
                - east
                - north

    """

    def run(self, body: dict, **kwargs):
        try:
            coordinates = [
                [
                    float(body[self.coordinate_keys[0]]),
                    float(body[self.coordinate_keys[1]]),
                ],
                [
                    float(body[self.coordinate_keys[2]]),
                    float(body[self.coordinate_keys[3]]),
                ],
            ]

            body["bbox"] = {
                "type": "envelope",
                "coordinates": coordinates,
            }

        except KeyError:
            LOGGER.warning("Unable to convert bbox.", exc_info=True)

        return body
