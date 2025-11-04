beat_schedule = {
    'process_outbox-every-10s': {
        'task': 'apps.worker.tasks.outbox.process_outbox',
        'schedule': 10.0,  # every 10 seconds
        'args': (5,), # limit
    },
    'ingest-new-listings-every-5m': {
        'task': 'apps.worker.tasks.ingest.run_ingest',
        'schedule': 300.0,  # every 5 minutes
        'args': (10,), # max_listings
    },
}
