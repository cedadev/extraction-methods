__author__ = "Rhys Evans"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


import logging
import re

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class StringTemplateExtract(ExtractionMethod):
    """

    Processor Name: ``string_join``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
        - ``key_list``: ``REQUIRED`` list of keys to convert to bbox array. Ordering is respected.
        - ``delimiter``: ``REQUIRED`` text delimiter to put between strings
        - ``key``: ``REQUIRED`` name of the key you would like to output
        - ``destructive``: Optional boolean false to retain original terms. ``DEFAULT``: True

    Example Configuration:


    .. code-block:: yaml

        - method: string_template
          template: {hello}/{goodbye}/{hello}/bonjour.html
          output_key: manifest_url

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not hasattr(self, "destructive"):
            self.destructive = True

    def run(self, body: dict, **kwargs):
        terms = re.findall("{(.*?)}", self.template)

        format_terms = {term: body[term] for term in terms}

        body[self.output_key] = self.template.format(**format_terms)

        return body
