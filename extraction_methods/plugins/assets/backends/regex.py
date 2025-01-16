# encoding: utf-8
"""
..  _regex:

RegexAssets
------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import glob
import logging

from pydantic import Field

from extraction_methods.core.extraction_method import SetInput, update_input
from extraction_methods.core.types import Input


LOGGER = logging.getLogger(__name__)


class RegexAssetsInput(Input):
    """Intake backend input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )


class RegexAssets(SetInput):
    """

    .. list-table::

        * - Processor Name
          - ``regex``

    Description:
        Takes an input string and a regex with
        named capture groups and returns a dictionary of the values
        extracted using the named capture groups.

    Configuration Options:
        - ``glob``: The regular expression to match against the filepath
        - ``glob_term``: The term to use for regular expression to match against the filepath


    Example configuration:
        .. code-block:: yaml

            - method: glob_assets
              inputs:
                glob: ^(?:[^_]*_){2}(?P<datetime>\d*)

    # noqa: W605
    """

    input_class = RegexAssetsInput

    @update_input
    def run(self, body: dict):

        for path in glob.iglob(self.input.input_term):
            yield {
                "href": path,
            }
