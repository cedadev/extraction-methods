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


import glob
import logging

# Python imports
from pathlib import Path

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class RegexAssetsExtract(ExtractionMethod):
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

    def run(self, body: dict, **kwargs) -> dict:
        assets = body.get("assets", {})

        if not hasattr(self, "glob"):
            self.glob = body[self.glob_term]

        for path in glob.iglob(self.glob):
            asset = {
                "href": path,
            }

            if hasattr(self, "extraction_methods"):
                for extraction_method in self.extraction_methods:
                    asset = extraction_method.run(asset)

            assets[Path(path).stem] = asset

        body["assets"] = assets

        return body
