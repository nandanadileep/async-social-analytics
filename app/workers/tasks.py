import time
from app.workers.celery_app import celery_app

@celery_app.task(bind=True)
def dummy_analysis_task(self, payload):
    try:
        time.sleep(5)
        return {
            "status": "ok",
            "payload": payload
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
