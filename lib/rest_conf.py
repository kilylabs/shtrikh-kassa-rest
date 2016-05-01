import kkm_conf

MONGO_URI = kkm_conf.MONGO_URI
DEBUG = kkm_conf.DEBUG

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

DOMAIN = {
    'report': {
        'schema': {
            'type': {
                'type': 'string',
                'allowed': ['x','z'],
                'required': True,
            }
        }
    },
    'checks': {
        'schema': {
            'client_name': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 32,
                'required': False,
            },
            'order_id': {
                'type': 'string',
                'minlength': 0,
                'maxlength': 32,
                'required': False,
            },
            'type': {
                'type': 'string',
                'allowed': ['sale','buy','sale_return','buy_return'],
                'required': False,
            },
            'subtype': {
                'type': 'string',
                'allowed': ['cash','card','special1','special2'],
                'required': False,
            },
            'barcode': {
                'type': 'number',
                'min': 0,
                'max': 9999999999999,
                'required': False,
            },
            'positions': {
                'type': 'list',
                'default': [],
                'items': {
                    'art': {
                        'type': 'string',
                        'minlength': 1,
                        'maxlength': 65,
                        'required': True,
                        },
                    'name': {
                        'type': 'string',
                        'minlength': 1,
                        'maxlength': 255,
                        'required': True,
                        },
                    'price': {
                        'type': 'float',
                        'min': 0.00,
                        'max': 999999.99,
                        'required': True,
                        },
                    'quantity': {
                        'type': 'number',
                        'min': 1,
                        'max': 9999,
                        'required': True,
                        },
                    'discount': {
                        'type': 'number',
                        'min': 0,
                        'max': 100,
                        'required': False,
                        },
                }
            }
        }
    }
}
