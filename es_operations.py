import json
import logging

from elasticsearch import Elasticsearch

import config
import extract_recipes


logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler()],
    format='%(asctime)s - %(levelname)s - %(process)s - %(message)s')



def search_items_in_es(es_object, index_name, search):
    """Search items in Elastic Search."""
    res = es_object.search(index=index_name, body=search)
    logging.info('Search result is: %s', res)
    return res


def create_index_in_es(es_object, index_name):
    """Create indexe in Elastic Search."""
    created = False
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(
                index=index_name, ignore=400, body=config.SETTINGS)
            logging.info('Created index: %s successfully', index_name)
        created = True
    except Exception as ex:
        logging.error(str(ex))
    finally:
        return created


def store_record_in_es(elastic_object, index_name, record):
    """Store records to Elastic Search."""
    is_stored = True
    try:
        outcome = elastic_object.index(
            index=index_name, doc_type='salads', body=record)
        logging.info('Record inserted to ES: %s', outcome)
    except Exception as ex:
        logging.error('Error in indexing data. %s', str(ex))
        is_stored = False
    finally:
        return is_stored


def connect_elasticsearch(host='localhost', port=9200):
    """Stablish connection to ElasticSearch."""
    es_conn = None
    es_conn = Elasticsearch([{'host': host, 'port': port}])
    if es_conn.ping():
        logging.info('Connected to ElasticSearch !')
    else:
        logging.info('Could not connect to Elasticsearch !')
    return es_conn


def close_elasticsearh_conn(es):
    """Close the existing ElasticSearch connection."""
    try:
        es.close()
        logging.info('Closed ElasticSearch connection.')
    except Exception as ex:
        logging.error('Unable to close ES connection. %s', str(ex))


if __name__ == '__main__':

    es = connect_elasticsearch()

    # recipes = extract_recipes.get_recipes()
    # for recipe in recipes:
    #     if es is None:
    #         logging.info(
    #             ('Not connected to Elastic Search, '
    #              'make sure Elastic Search is up and running.'))
    #         continue
    #     if create_index_in_es(es, 'recipes'):
    #         out = store_record_in_es(es, 'recipes', recipe)
    #         logging.info('Data indexed successfully')

    search_object = {
        '_source': ['title'],  # will return records with only title prop
        'query': {
            'range': {
                'calories': {
                    'gte': 200  # all records where calories > 200
                }
            }
        }
    }
    output = search_items_in_es(es, 'recipes', json.dumps(search_object))
    close_elasticsearh_conn(es)
