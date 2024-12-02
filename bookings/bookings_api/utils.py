from slicerepublic.dateutil import is_within_date_range


def is_paid_booking(mbo_client_service, class_date):
	return is_within_date_range(mbo_client_service.active_date, mbo_client_service.expiration_date, class_date)
