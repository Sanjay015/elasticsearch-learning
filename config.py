"""Configurations and constant variables here."""

SETTINGS = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'salads': {
            'dynamic': 'strict',
            'properties': {
                'title': {
                    'type': 'text'
                },
                'submitter': {
                    'type': 'text'
                },
                'description': {
                    'type': 'text'
                },
                'calories': {
                    'type': 'float'
                },
                'ingredients': {
                    'type': 'nested',
                    'properties': {
                        'step': {'type': 'text'}
                    }
                },
                'url': {
                    'type': 'text'
                },
            }
        }
    }
}