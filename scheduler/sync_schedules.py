from datetime import timedelta
from django.db import transaction
from classes.class_manager import handle_schedule_from_mbo
from classes.models import Program
from mind_body_service.classes_api import get_class_schedules
from slicerepublic import dateutil


@transaction.atomic
def sync_schedules(mbo_site_id, force_update=False):
	program_ids = list(Program.objects.get_integrated_program_id_list_by_mbo_site_id(mbo_site_id))

	if len(program_ids) == 0:
		print("No program ids found!")
		return

	start_date = dateutil.utcnow()

	end_date = dateutil.utcnow_plus(timedelta(days=14))
	get_schedules_result = get_class_schedules(start_date=start_date, end_date=end_date, mbo_site_id=mbo_site_id, mbo_program_ids=program_ids)

	result_count = get_schedules_result.ResultCount
	total_page_count = get_schedules_result.TotalPageCount

	if result_count > 0:
		for schedule in get_schedules_result.ClassSchedules.ClassSchedule:
			#print("Handling schedule {}".format(schedule.ID))
			handle_schedule_from_mbo(schedule, mbo_site_id)

	if total_page_count > 0:
		for page in range(1, total_page_count):
			sync_schedules_page_by_page(start_date, end_date, mbo_site_id, program_ids, page)


def sync_schedules_page_by_page(start_date, end_date, mbo_site_id, program_ids, page):
	get_schedules_result = get_class_schedules(start_date=start_date, end_date=end_date, mbo_site_id=mbo_site_id, mbo_program_ids=program_ids, page=page)
	result_count = get_schedules_result.ResultCount
	if result_count > 0:
		for schedule in get_schedules_result.ClassSchedules.ClassSchedule:
			#print("Handling schedule {}".format(schedule.ID))
			handle_schedule_from_mbo(schedule, mbo_site_id)
