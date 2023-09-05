# encoding: utf-8
"""
..  _elasticsearch-extract:

Elasticsearch Extract
------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging

# Third party imports
from elasticsearch import Elasticsearch

from extraction_methods.core.extraction_method import ExtractionMethod

LOGGER = logging.getLogger(__name__)


class ElasticsearchExtract(ExtractionMethod):
    """
    Description:
        Using an ID. Generate a summary of information for higher level entities.

    Configuration Options:
        - ``index``: Name of the index holding the STAC entities
        - ``id_term``: Term used for agregating the STAC entities
        - ``session_kwargs``: Session parameters passed to
        `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_
        - ``bbox``: list of terms for which their aggregate bbox should be returned.
        - ``min``: list of terms for which the minimum of their aggregate should be returned.
        - ``max``: list of terms for which the maximum of their aggregate should be returned.
        - ``sum``: list of terms for which the sum of their aggregate should be returned.
        - ``list``: list of terms for which a list of their aggregage should be returned.

    Configuration Example:

        .. code-block:: yaml

                name: elasticsearch
                inputs:
                    index: ceda-index
                    id_term: item_id
                    connection_kwargs:
                      hosts: ['host1:9200','host2:9200']
                    bbox:
                      - bbox
                    min:
                      - start_time
                    max:
                      - end_time
                    sum:
                      - size
                    list:
                      - term1
                      - term2
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "connection_kwargs"):
            self.es = Elasticsearch(**self.connection_kwargs)

        if not hasattr(self, "request_tiemout"):
            self.request_tiemout = 15

    @staticmethod
    def bbox_query(facet: str) -> dict:
        """
        Query to retrieve the BBOX from items
        """
        return {"bbox": {"geo_bounds": {"field": facet, "wrap_longitude": True}}}

    @staticmethod
    def facet_composite_query(facet: str) -> dict:
        """
        Generate the composite aggregation for the facet
        :param facet: Facet to aggregate on
        """
        return {
            facet: {
                "composite": {
                    "sources": [
                        {facet: {"terms": {"field": f"properties.{facet}.keyword"}}}
                    ],
                    "size": 100,
                }
            }
        }

    @staticmethod
    def min_query(facet: str) -> dict:
        """
        Query to retrieve the minimum value from docs
        """
        return {facet: {"min": {"field": f"properties.{facet}"}}}

    @staticmethod
    def max_query(facet: str) -> dict:
        """
        Query to retrieve the maximum value from docs
        """
        return {facet: {"max": {"field": f"properties.{facet}"}}}

    @staticmethod
    def sum_query(facet: str) -> dict:
        """
        Query to retrieve the sum of the values from docs
        """
        return {facet: {"sum": {"field": f"properties.{facet}"}}}

    def extract_facet(self, facets: list):
        """
        Function to extract the given facets from the aggregation
        """
        for facet in facets:
            if facet in self.aggregations.keys():
                if "value_as_string" in self.aggregations[facet].keys():
                    value = self.aggregations[facet]["value_as_string"]

                else:
                    value = self.aggregations[facet]["value"]

                self.metadata[facet] = value

    def extract_first_facet(self, facets: list):
        """
        Function to extract the given default facets from the first hit
        """
        properties = self.hits[0]["_source"]["properties"]

        for facet in facets:
            if facet in properties.keys():
                self.metadata[facet] = properties[facet]

    def extract_facet_list(self, facets: list):
        """
        Function to extract the lists of given facets from the aggregation
        """
        next_query = self.base_query
        items = self.aggregations

        while True:
            for facet in facets:
                if facet in items.keys():
                    aggregation = items[facet]

                    self.metadata[facet].extend(
                        [bucket["key"][facet] for bucket in aggregation["buckets"]]
                    )

                    if hasattr(aggregation, "after_key"):
                        next_query["aggs"] |= self.query["aggs"][facet]
                        next_query["aggs"][facet]["composite"]["sources"]["after"] = {
                            facet: aggregation["after_key"][facet]
                        }

            if next_query == self.base_query:
                break

            else:
                result = self.es.search(index=self.index, body=next_query)
                items = result["aggregations"].items()

    def construct_base_query(self, key: str, uri: str) -> dict:
        """
        Base query to filter the results to a single collection

        :param uri: Collection to restrict results to
        """
        self.base_query = {
            "query": {
                "bool": {
                    "must_not": [{"term": {"categories.keyword": {"value": "hidden"}}}],
                    "must": [{"term": {f"{key}.keyword": {"value": uri}}}],
                }
            },
            "aggs": {},
        }

    def construct_query(self):
        """
        Function to create the initial elasticsearch query
        """
        self.query = self.base_query

        if hasattr(self, "bbox"):
            for bbox_term in self.bbox:
                self.query["aggs"].update(self.bbox_query(bbox_term))

        if hasattr(self, "min"):
            for min_term in self.min:
                self.query["aggs"].update(self.min_query(min_term))

        if hasattr(self, "max"):
            for max_term in self.max:
                self.query["aggs"].update(self.max_query(max_term))

        if hasattr(self, "sum"):
            for sum_term in self.sum:
                self.query["aggs"].update(self.sum_query(sum_term))

        if hasattr(self, "list"):
            for list_term in self.list:
                self.query["aggs"].update(self.facet_composite_query(list_term))

    def extract_metadata(self):
        """
        Function to extract the required metadata from the returned query result
        """
        if hasattr(self, "first"):
            self.extract_first_facet(self.first)

        if hasattr(self, "bbox"):
            self.extract_facet(self.bbox)

        if hasattr(self, "min"):
            self.extract_facet(self.min)

        if hasattr(self, "max"):
            self.extract_facet(self.max)

        if hasattr(self, "sum"):
            self.extract_facet(self.sum)

        if hasattr(self, "list"):
            self.extract_facet_list(self.list)

    def run(self, body: dict, **kwargs) -> dict:
        self.metadata = body

        self.construct_base_query(self.id_term, body["uri"])

        self.construct_query()

        LOGGER.info("Elasticsearch query: %s", self.query)

        # Run query
        print(self.query)
        result = self.es.search(
            index=self.index, body=self.query, timeout=f"{self.request_tiemout}s"
        )

        print(result)

        self.hits = result["hits"]["hits"]

        self.aggregations = result["aggregations"]

        # Extract metadata
        self.extract_metadata()

        return self.metadata
