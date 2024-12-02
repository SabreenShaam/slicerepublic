from model_mommy.recipe import Recipe, foreign_key
from classes.models import SliceClass, SessionType, Program
from datetime import datetime
from slicerepublic.dateutil import make_utc
from staff.mommy_recipes import staff
from venues.mommy_recipes import location, external_studio, studio

session_type = Recipe(
	SessionType,
	name='60 min. Pilates',
	mbo_session_type_id=24,
	mbo_site_id=-99,
	program_id=1,
	num_deducted=1,
)

program = Recipe(
	Program,
	mbo_program_id=26,
	site=foreign_key(external_studio),
	schedule_type='Drop in',
	cancel_off_set='20',
	opens='14',
	is_integrated=True,
)

slice_class_external = Recipe(
	SliceClass,
	name='Barre',
	mbo_class_id=20096,
	studio=foreign_key(external_studio),
	mbo_last_updated=make_utc(datetime(2016, 6, 23, 18, 30, 2, 983000)),
	description='Stripping classical Pilates back to the basics,..',
	is_cancelled=False,
	staff=foreign_key(staff),
	session_type=foreign_key(session_type),
	start_date=make_utc(datetime(2016, 6, 30)).date(),
	end_date=make_utc(datetime(2016, 6, 30)).date(),
	start_time=make_utc(datetime(2016, 6, 24, 18, 30)).time(),
	end_time=make_utc(datetime(2015, 7, 2, 18, 30)).time(),
	location=foreign_key(location),
	is_active=True,
)

slice_class = Recipe(
	SliceClass,
	name='Barre',
	mbo_class_id=20096,
	studio=foreign_key(studio),
	mbo_last_updated=make_utc(datetime(2016, 6, 23, 18, 30, 2, 983000)),
	description='Stripping classical Pilates back to the basics,..',
	is_cancelled=False,
	staff=foreign_key(staff),
	session_type=foreign_key(session_type),
	start_date=make_utc(datetime(2016, 7, 2)).date(),
	end_date=make_utc(datetime(2016, 7, 2)).date(),
	start_time=make_utc(datetime(2016, 6, 24, 18, 30)).time(),
	end_time=make_utc(datetime(2015, 7, 2, 18, 30)).time(),
	location=foreign_key(location),
	is_active=True,
)


slice_class_home = Recipe(
	SliceClass,
	name='Barre',
	mbo_class_id=20096,
	studio=foreign_key(studio),
	mbo_last_updated=make_utc(datetime(2016, 6, 23, 18, 30, 2, 983000)),
	description='Stripping classical Pilates back to the basics,..',
	is_cancelled=False,
	staff=foreign_key(staff),
	session_type=foreign_key(session_type),
	start_date=make_utc(datetime(2016, 7, 2)).date(),
	end_date=make_utc(datetime(2016, 7, 2)).date(),
	start_time=make_utc(datetime(2016, 6, 24, 18, 30)).time(),
	end_time=make_utc(datetime(2015, 7, 2, 18, 30)).time(),
	location=foreign_key(location),
	is_active=True,
)