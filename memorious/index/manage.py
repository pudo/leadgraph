import logging

from memorious.core import es, es_index
from memorious.model import Schema
from memorious.index.crossref import CROSSREF_TYPE
from memorious.index.mapping import LINK_MAPPING, ENTITY_MAPPING
from memorious.index.mapping import CROSSREF_MAPPING

log = logging.getLogger(__name__)


def init_search():
    log.info("Creating ElasticSearch index and mapping...")
    es.indices.delete(es_index, ignore=[404, 400])
    es.indices.create(es_index, body={
        'mappings': {
            Schema.LINK: LINK_MAPPING,
            Schema.ENTITY: ENTITY_MAPPING,
            CROSSREF_TYPE: CROSSREF_MAPPING
        }
    }, ignore=[400, 404])
    es.indices.open(index=es_index, ignore=[400, 404])


def upgrade_search():
    """Add any missing properties to the index mappings."""
    es.indices.put_mapping(index=es_index, body=LINK_MAPPING,
                           doc_type=Schema.LINK)
    es.indices.put_mapping(index=es_index, body=ENTITY_MAPPING,
                           doc_type=Schema.ENTITY)
    es.indices.put_mapping(index=es_index, body=CROSSREF_MAPPING,
                           doc_type=CROSSREF_TYPE)
