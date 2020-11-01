import json

from delegate_emr import delegate_emr
from delegate_es_indexer import delegate_es_indexer


def start(event, context):
    print(event)

    event = unwrap_if_sqs(event)

    type = event['type']

    if type == 'emr':
        response = delegate_emr(event, context)
    elif type == 'es':
        response = delegate_es_indexer(event, context)
    else:
        return {'Result': 400, 'Type': type}

    return {
        'Result': 200,
        'Type': type,
        'Response': response
    }


def unwrap_if_sqs(event):
    if 'Records' in event and len(event['Records']) == 1:
        return json.loads(event['Records'][0]['body'])
    else:
        return event