from celery.task import task
from bookings.bookings_core.booking_manager import get_user_bookings_by_user_first_name, cancel_bookings
import datetime
from mind_body_service.classes_api import update_client_visits
from django.conf import settings
import redis


@task
def cancel_test_user_bookings(force_update=False, mbo_site_id=None):
    redis_lock = redis.Redis().lock('syn_classes', timeout=settings.REDIS_LOCK_TIMEOUT)
    have_lock = False
    try:
        have_lock = redis_lock.acquire(blocking=False)
        if have_lock:
            try:
                print("Starting to sync cancel_user_bookings")
                time_now = datetime.datetime.now()
                last_synced_time = datetime.datetime.now() - datetime.timedelta(minutes=60)

                bookings = get_user_bookings_by_user_first_name('Test', [last_synced_time, time_now])
                cancel_bookings(bookings)
            except Exception as e:
                message = e.args[0]
                print('Sync failed : {}'.format(message))

    except Exception as e:
        pass
    finally:
        if have_lock:
            redis_lock.release()

