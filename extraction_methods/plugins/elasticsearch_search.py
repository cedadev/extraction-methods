# encoding: utf-8
""" """
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging
from typing import Any

# Third party imports
from elasticsearch import Elasticsearch as Elasticsearch_client
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class ElasticsearchSearchInput(Input):
    """
    Model for Elasticsearch Assets Backend Input.
    """

    index: str = Field(
        description="Index to search on.",
    )
    client_kwargs: dict[str, Any] = Field(
        default={},
        description="Client kwargs.",
    )
    search_kwargs: dict[str, Any] = Field(
        default={"timeout": "60s"},
        description="Search kwargs.",
    )
    body: dict[str, Any] = Field(
        description="Body of search request.",
    )
    output_key: str = Field(
        default="es_result",
        description="key to output to.",
    )


class ElasticsearchSearchExtract(ExtractionMethod):
    """
    **Method name:** ``elasticsearch_search``

    Search Elasticsearch.


    Example Configuration:
        .. code-block:: yaml

            - method: elasticsearch
              inputs:
                index: ceda-index
                client_kwargs:
                  hosts: ['host1:9200','host2:9200']
                search_kwargs:
                  timeout: 100s
                body:
                  query:
                    regex: $regex_value
                  _source:
                    - path
    """

    input_class = ElasticsearchSearchInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        es = Elasticsearch_client(**self.input.client_kwargs)

        # Run search
        result = es.search(
            index=self.input.index, body=self.input.body, **self.input.search_kwargs
        )

        body[self.input.output_key] = result["hits"]["hits"]

        return body
