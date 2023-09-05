# encoding: utf-8
"""
..  _regex:

Regex
------
"""
__author__ = "Rhys Evans"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


# Python imports
import logging

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class DefaultExtract(ExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``default``

    Description:
        Takes a set of default facets.

    Configuration Options:
        - ``defaults``: Dictionary of defaults to be added


    Example configuration:
        .. code-block:: yaml

            - method: default
              inputs:
                defaults:
                  mip_era: CMIP6

    """

    def run(self, body: dict, **kwargs) -> dict:
        body = body | self.defaults

        return body
