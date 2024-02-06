# encoding: utf-8
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import os

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class BasenameExtract(ExtractionMethod):
    """

    Processor Name: ``basename``

    Description:
        Takes a file path and returns the filename using `os.path.basename`.

    Example Configuration:

    .. code-block:: yaml

        - method: basename

    """

    def run(self, body: dict, **kwargs) -> dict:
        body["basename"] = os.path.basename(body["uri"])

        return body
