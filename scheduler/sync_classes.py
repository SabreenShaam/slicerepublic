from mind_body_service import classes_api
from datetime import datetime
from classes.class_manager import handle_class_from_mbo, handle_class_deactivation
from classes.models import Program, SliceClass
from venues.models import Studio
from django.db import transaction


@transaction.atomic
def sync_classes(start, end, mbo_site_id, force_update=False):
    synced_class_ids = []
    start_time = datetime.now()

    program_ids = list(Program.objects.get_integrated_program_id_list_by_mbo_site_id(mbo_site_id))

    if len(program_ids) == 0:
        print("No program ids found!")
        return

    studio = Studio.objects.get_studio_by_mbo_site_id(mbo_site_id)
    slice_classes = SliceClass.objects.get_classes_by_date_range_and_studio(start.date(), end.date(), [studio.id])

    get_classes_result = classes_api.get_classes(mbo_site_id=mbo_site_id, start_date=start.date(), end_date=end.date(),
                                                 program_ids=program_ids)
    status = get_classes_result.Status
    if status == 'InvalidCredentials':
        raise Exception('InvalidCredentials')
    result_count = get_classes_result.ResultCount
    total_page_count = get_classes_result.TotalPageCount
    current_page_index = get_classes_result.CurrentPageIndex

    if len(get_classes_result.Classes) == 0:
        return

    print('Found {} classes'.format(result_count))
    print('Total pages {}'.format(total_page_count))

    for mbo_class in get_classes_result.Classes[0]:
        handle_class_from_mbo(mbo_class, slice_classes, studio, synced_class_ids)

    if total_page_count > 1:
        for page in range(1, total_page_count):
            sync_classes_by_page(start, end, page, slice_classes, studio, program_ids, synced_class_ids, force_update=False)

    end_time = datetime.now() - start_time

    current_class_ids = [slice_class.id for slice_class in slice_classes]
    if len(synced_class_ids) > 0:
        handle_class_deactivation(synced_class_ids, current_class_ids)

    print("Time consumed : {}".format(end_time.total_seconds()))


def sync_classes_by_page(start, end, page, slice_classes, studio, program_ids, synced_class_ids, force_update=False):
    get_classes_result = classes_api.get_classes(mbo_site_id=studio.mbo_site_id, start_date=start.date(), end_date=end.date(),
                                                 page=page, program_ids=program_ids)

    current_page_index = get_classes_result.CurrentPageIndex
    print('Getting {} page'.format(current_page_index))

    if len(get_classes_result.Classes) == 0:
        return

    for mbo_class in get_classes_result.Classes[0]:
        handle_class_from_mbo(mbo_class, slice_classes, studio, synced_class_ids)

    print('Completed page {}'.format(page))
