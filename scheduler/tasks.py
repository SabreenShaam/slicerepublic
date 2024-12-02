from datetime import timedelta

from celery.task import task
from django.conf import settings
import redis
from celery import chain

from scheduler.sync_schedules import sync_schedules
from slicerepublic.dateutil import utcnow, utcnow_plus
from venues.models import Studio
from .sync_classes import sync_classes
from .sync_venues import sync_locations, sync_resources
from bookings.bookings_core import booking_manager


@task
def sync_mbo_classes_task(start=None, days=14, force_update=False, mbo_site_id=None):
    if not start:
        start = utcnow()

    redis_lock = redis.Redis().lock('syn_classes', timeout=settings.REDIS_LOCK_TIMEOUT)
    have_lock = False

    try:
        have_lock = redis_lock.acquire(blocking=False)
        if have_lock:
            end = utcnow_plus(timedelta(days=days))
            if mbo_site_id:
                site_ids = [mbo_site_id]
            else:
                site_ids = [s['mbo_site_id'] for s in Studio.objects.get_all_active_mbo_studios().values('mbo_site_id')]
            if not site_ids:
                print('No sites found')
                return
            for site_id in site_ids:
                try:
                    print("Starting to sync site {}".format(site_id))
                    sync_classes(start, end, site_id, force_update)
                except Exception as e:
                    message = e.args[0]
                    print('Sync failed : {}'.format(message))
    except Exception as e:
        pass
    finally:
        if have_lock:
            redis_lock.release()


@task
def sync_mbo_schedules_task(force_update=False, mbo_site_id=None):
    start = utcnow()

    redis_lock = redis.Redis().lock('syn_classes', timeout=settings.REDIS_LOCK_TIMEOUT)
    have_lock = False

    try:
        have_lock = redis_lock.acquire(blocking=False)
        if have_lock:
            if mbo_site_id:
                site_ids = [mbo_site_id]
            else:
                site_ids = [s['mbo_site_id'] for s in Studio.objects.get_all_active_mbo_studios().values('mbo_site_id')]
            if not site_ids:
                print('No sites found')
                return
            for site_id in site_ids:
                try:
                    print("Starting to sync schedules in site {}".format(site_id))
                    sync_schedules(site_id)
                except Exception as e:
                    message = e.args[0]
                    print('Sync failed : {}'.format(message))
    except Exception as e:
        pass
    finally:
        if have_lock:
            redis_lock.release()


@task
def sync_mbo_locations_task(force_update=False, mbo_site_id=None):
    start = utcnow()

    redis_lock = redis.Redis().lock('syn_classes', timeout=settings.REDIS_LOCK_TIMEOUT)
    have_lock = False

    try:
        have_lock = redis_lock.acquire(blocking=False)
        if have_lock:
            if mbo_site_id:
                site_ids = [mbo_site_id]
            else:
                site_ids = [s['mbo_site_id'] for s in Studio.objects.get_all_active_mbo_studios().values('mbo_site_id')]
            if not site_ids:
                print('No sites found')
                return
            for site_id in site_ids:
                try:
                    print("Starting to sync locations in site {}".format(site_id))
                    sync_locations(site_id)
                except Exception as e:
                    message = e.args[0]
                    print('Sync failed : {}'.format(message))
    except Exception as e:
        pass
    finally:
        if have_lock:
            redis_lock.release()


@task
def sync_mbo_resources_task(force_update=False, mbo_site_id=None):
    start = utcnow()

    redis_lock = redis.Redis().lock('syn_classes', timeout=settings.REDIS_LOCK_TIMEOUT)
    have_lock = False

    try:
        have_lock = redis_lock.acquire(blocking=False)
        if have_lock:
            if mbo_site_id:
                site_ids = [mbo_site_id]
            else:
                site_ids = [s['mbo_site_id'] for s in Studio.objects.get_all_active_mbo_studios().values('mbo_site_id')]
            if not site_ids:
                print('No sites found')
                return
            for site_id in site_ids:
                try:
                    print("Starting to sync resources in site {}".format(site_id))
                    sync_resources(site_id)
                except Exception as e:
                    message = e.args[0]
                    print('Sync failed : {}'.format(message))
    except Exception as e:
        pass
    finally:
        if have_lock:
            redis_lock.release()


@task
def sync_mbo_resources():
    sync_resources = sync_mbo_resources_task.si()
    sync_locations = sync_mbo_locations_task.si()
    sync_schedules = sync_mbo_schedules_task.si()
    sync_classes = sync_mbo_classes_task.si()

    pipeline = chain(sync_resources, sync_locations, sync_schedules, sync_classes)()


@task
def handle_unpaid_bookings():
    print('Handling unpaid bookings')
    booking_manager.handle_unpaid_bookings()
    print('Finished handling unpaid bookings')
