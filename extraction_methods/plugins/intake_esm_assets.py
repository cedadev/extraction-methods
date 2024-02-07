# encoding: utf-8
"""
Intake Input
-----------------

Uses an `Intake catalog <https://intake.readthedocs.io/>`_
as a source for file objects.

**Plugin name:** ``intake_esm``

.. list-table::
    :header-rows: 1

    * - Option
      - Value Type
      - Description
    * - ``uri``
      - ``string``
      - ``REQUIRED`` The URI of a path or URL to an ESM collection JSON file.
    * - ``object_path_attr``
      - ``string``
      - ``REQUIRED`` The column header which contains the URI to
        the file object.
    * - ``catalog_kwargs``
      - ``dict``
      - Optional kwargs to pass to
        `intake.open_esm_datastore
        <https://intake-esm.readthedocs.io/en/latest
        /api.html#intake_esm.core.esm_datastore>`_
    * - ``search_kwargs``
      - ``dict``
      - Optional kwargs to pass to `esm_datastore.search
        <https://intake-esm.readthedocs.io/en/latest
        /api.html#intake_esm.core.esm_datastore.search>`_


Example Configuration:
    .. code-block:: yaml

        inputs:
            - method: intake_catalog
              uri: test_directory

"""
__author__ = "Richard Smith"
__date__ = "23 Sep 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from datetime import datetime
from pathlib import Path

# Thirdparty imports
import intake

# Package imports
from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class IntakeESMAssetExtract(ExtractionMethod):
    """
    Performs an os.walk to provide a stream of paths for procesing.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.uri = kwargs["uri"]

        self.object_attr = kwargs["object_path_attr"]

        self.intake_kwargs = kwargs.get("catalog_kwargs", {})
        self.search_kwargs = kwargs.get("search_kwargs")

    def open_catalog(self):
        """Open the ESM catalog and perform a search, if required."""
        LOGGER.info(f"Opening catalog {self.uri}")
        catalog = intake.open_esm_datastore(self.uri, **self.intake_kwargs)

        if self.search_kwargs:
            catalog = catalog.search(**self.search_kwargs)

        LOGGER.info(f"Found {len(catalog.df)} items")
        return catalog

    def update_search_kwargs(self, body:dict):
      for search_kwarg_key, search_kwarg_value in self.search_kwargs.items():
        if search_kwarg_value[0] == self.exists_key:
                self.search_kwargs[search_kwarg_key] = body[search_kwarg_value[1:]]

    def run(self, body: dict, **kwargs) -> dict:

        self.update_search_kwargs(body)
        catalog = self.open_catalog()

        assets = body.get("assets", {})

        for _, row in catalog.df.iterrows():
            href = getattr(row, self.object_attr)
            asset = {
                "href": href,
            }

            if hasattr(self, "extraction_methods"):
                for extraction_method in self.extraction_methods:
                    asset = extraction_method.run(asset)

            assets[Path(href).name] = asset

        body["assets"] = assets

        return body