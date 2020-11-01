import requests

from shared import env

def delegate_es_indexer(event, context):
    
    job = event['job']
    es_host = env('ES_HOST')
    
    print('ES Index: {job} to {host}'.format(job=job, host=es_host))
    
    did_delete = _delete_index_if_exists(job)
    did_create = _create_index(job)
    
    return {
        'Index': job,
        'Deleted': did_delete,
        'Created': did_create
    }
    
def _create_index(es_index):
    es_host = env('ES_HOST')
    
    if es_index in index_options:
        body = index_options[es_index]
        r = requests.put('https://{domain}/{index}'.format(domain=es_host, index=es_index), headers=headers, data=body)
        return True
    else:
        return False
    
def _delete_index_if_exists(es_index):
    es_host = env('ES_HOST')
    
    url = 'https://{domain}/{index}'.format(domain=es_host, index=es_index)
    
    r = requests.get(url, headers=headers)
    
    if r.status_code == 404:
        print('Index does not exist: {index}'.format(index=es_index))
        return False
    else:
        print('Deleting index: {index}'.format(index=es_index))
        rd = requests.delete(url, headers=headers)
        if rd.status_code in range(200, 300):
            return True

    return False

headers = {
    'Content-Type': 'application/json'
}

index_options = {

    'hh2_candidates': """
        {
            "mappings": {
                "dynamic": false,
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "firstName": {
                        "type": "keyword"
                    },
                    "fullName": {
                        "type": "keyword"
                    },
                    "lastName": {
                        "type": "keyword"
                    },
                    "monthsExperience": {
                        "type": "integer"
                    },
                    "jobHistories": {
                        "type": "nested",
                        "properties": {
                            "sequence": {
                                "type": "integer"
                            },
                            "companyId": {
                                "type": "integer"
                            },
                            "companyName": {
                                "type": "keyword"
                            },
                            "title": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            },
                            "start": {
                                "type": "keyword"
                            },
                            "end": {
                                "type": "keyword"
                            },
                            "location": {
                                "type": "keyword"
                            },
                            "monthsExperience": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        }
    """,

    'hh2_companies': """
        {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "ngram_autocomplete": {
                            "tokenizer": "my_tokenizer",
                            "filter": [
                                "lowercase"
                            ]
                        }
                    },
                    "tokenizer": {
                        "my_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 30,
                            "token_chars": [
                                "letter",
                                "digit",
                                "whitespace",
                                "punctuation"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "dynamic": false,
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "keyword",
                        "fields": {
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "ngram_autocomplete"
                            }
                        }
                    },
                    "candidateCount": {
                        "type": "integer"
                    }
                }
            }
        }
    """
}