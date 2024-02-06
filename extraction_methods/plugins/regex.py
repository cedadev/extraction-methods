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
import re

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class RegexExtract(ExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``regex``

    Description:
        Takes an input string and a regex with
        named capture groups and returns a dictionary of the values
        extracted using the named capture groups.

    Configuration Options:
        - ``regex``: The regular expression to match against the filepath


    Example configuration:
        .. code-block:: yaml

            - method: regex
              inputs:
                regex: ^(?:[^_]*_){2}(?P<datetime>\d*)

    # noqa: W605
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = rf"{self.regex}"

        if not hasattr(self, "input_term"):
            self.input_term = "uri"

    def run(self, body: dict, **kwargs) -> dict:
        result = re.search(self.regex, body[self.input_term])

        if result:
            body = body | result.groupdict()

        else:
            LOGGER.debug("No matches found for regex extract")

        return body
