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
import re

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class CategoriesExtract(ExtractionMethod):
    """

    .. list-table::

        * - Processor Name
          - ``catagories``

    Description:
        Takes a list of catagory label and associated regex.

    Configuration Options:
        - ``catagories``: list of dictionaries containing label and regex

    Example configuration:
        .. code-block:: yaml

            - method: catagories
              inputs:
                catagories:
                  - label: metadata
                    regex: README
                  - label: hidden
                    regex: /\/.

    # noqa: W605
    """

    def get_category(self, uri, label, regex):
        """

        :param uri:
        :param label:
        :param regex:
        :return:

        """

        m = re.search(regex, uri)

        if not m:
            label = None

        return label

    def run(self, body: dict, **kwargs) -> dict:
        result = set()

        for category in self.categories:
            label = self.get_category(body["uri"], **category)
            if label:
                result.add(label)

        body["catagories"] = list(result) or ["data"]

        return body
