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


import glob
import logging
import os

# Python imports
from datetime import datetime
from pathlib import Path

import magic

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
        - ``regex``: The regular expression to match against the filepath


    Example configuration:
        .. code-block:: yaml

            - method: regex
              inputs:
                regex: ^(?:[^_]*_){2}(?P<datetime>\d*)

    # noqa: W605
    """

    def run(self, body: dict, **kwargs) -> dict:
        assets = body.get("assets", [])

        for path in glob.iglob(self.regex):
            stats = os.stat(path)
            assets.append(
                {
                    Path(path).stem: {
                        "href": path,
                        "role": self.role,
                        "type": magic.from_file(path, mime=True),
                        "last_modified": datetime.fromtimestamp(
                            stats.st_mtime
                        ).isoformat(),
                        "size": getattr(stats, "st_size"),
                    }
                }
            )

        body["assets"] = assets

        return body
