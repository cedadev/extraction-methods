# encoding: utf-8
""" """
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging
from typing import Any, Iterator

# Third party imports
from elasticsearch import Elasticsearch as Elasticsearch_client
from pydantic import Field

from extraction_methods.core.extraction_method import Backend, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class ElasticsearchAssetsInput(Input):
    """
    Model for Elasticsearch Assets Backend Input.
    """

    index: str = Field(
        description="Elasticsearch index to search on.",
    )
    client_kwargs: dict[str, Any] = Field(
        default={},
        description="Elasticsearch connection kwargs.",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout for search.",
    )
    body: dict[str, Any] = Field(
        description="Body for Elasticsearch search request.",
    )
    href_term: str = Field(
        default="path",
        description="term to use for href.",
    )


class ElasticsearchAssets(Backend):
    """
    **Method name:** ``elasticsearch_assets``

    Using an ID. Generate a summary of information for higher level entities.


    Example Configuration:
        .. code-block:: yaml

            - name: elasticsearch
              inputs:
                index: ceda-index
                id_term: item_id
                client_kwargs:
                    hosts: ['host1:9200','host2:9200']
                fields:
                    - roles
    """

    input_class = ElasticsearchAssetsInput

    @update_input
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:

        es = Elasticsearch_client(**self.input.client_kwargs)

        # Run search
        result = es.search(
            index=self.input.index,
            body=self.input.body,
            timeout=f"{self.input.request_timeout}s",
        )

        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            source["href"] = source.pop(self.input.href_term)

            yield source
