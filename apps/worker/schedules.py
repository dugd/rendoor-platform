beat_schedule = {
    "process-outbox-every-10s": {
        "task": "apps.worker.tasks.notify.process_outbox",
        "schedule": 10.0,
        "args": (5,),
    },
}
