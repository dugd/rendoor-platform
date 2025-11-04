beat_schedule = {
    'process_outbox-every-10s': {
        'task': 'apps.worker.tasks.outbox.process_outbox',
        'schedule': 10.0,  # every 10 seconds
        'args': (5,), # limit
    },
}
