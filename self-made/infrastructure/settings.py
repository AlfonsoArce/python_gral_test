import logging

mode = 'dev'
run = 'debug'

# TODO: Review platform (OS) compatibility
conf = {
    'prod': {
        'db_alias': 'hawkSystem_db',
        'db_name': 'hawkSystem_db',
        'log_level': logging.WARNING,
        'files_root': '/Volumes/data/1.business/2.hawkexpress/hawksystem/storage/email_order/attachments'
    },
    'debug': {
        'db_alias': 'hawkSystem_db',
        'db_name': 'hawkSystem_db',
        'log_level': logging.DEBUG,
        'files_root': '/Volumes/data/1.business/2.hawkexpress/hawksystem/storage/email_order/attachments'
    },
    'dev': {
        'db_alias': 'hawkSystem_dev',
        'db_name': 'hawkSystem_dev',
        'log_level': logging.DEBUG,
        'files_root': '/Volumes/data/1.business/2.hawkexpress/hawksystem/storage/email_order/attachments'
    }
}
