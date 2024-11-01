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
    * - ``href_term``
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

# Thirdparty imports
import intake
from pydantic import Field

from extraction_methods.core.extraction_method import Input, SetInput, update_input

LOGGER = logging.getLogger(__name__)


class IntakeESMAssetsInput(Input):
    """Intake backend input model."""

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    href_term: str = Field(
        default="path",
        description="term to use for href.",
    )
    datastore_kwargs: dict = Field(
        default={},
        description="kwargs to open datastore.",
    )
    search_kwargs: dict = Field(
        default={},
        description="kwargs for search.",
    )


class IntakeESMAssets(SetInput):
    """
    Performs Search on intake catalog to provide a stream of assets for procesing.
    """

    input_class = IntakeESMAssetsInput

    @update_input
    def run(self, body: dict):
        catalog = intake.open_esm_datastore(self.input.input_term, **self.input.datastore_kwargs)

        if search_kwargs := self.input.search_kwargs:
            catalog = catalog.search(**search_kwargs)

        for _, row in catalog.df.iterrows():
            if href := getattr(row, self.input.href_term):
                yield {
                    "href": href,
                }
