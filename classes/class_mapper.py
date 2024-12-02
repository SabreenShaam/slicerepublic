from slicerepublic.dateutil import make_utc
from slicerepublic.html_stripper import strip_tags
from .models import SessionType, Program, Schedule


def map_values_from_mbo_class_to_slice_class(mbo_class, slice_class, staff, mbolocation, session_type, studio):

    slice_class.name = mbo_class.ClassDescription.Name
    slice_class.mbo_class_id = mbo_class.ID
    slice_class.studio = studio

    slice_class.mbo_last_updated = make_utc(mbo_class.ClassDescription.LastUpdated)

    if mbo_class.ClassDescription.Description:
        slice_class.description = strip_tags(mbo_class.ClassDescription.Description)

    slice_class.is_cancelled = mbo_class.IsCanceled
    slice_class.staff = staff
    slice_class.session_type = session_type
    slice_class.start_date = make_utc(mbo_class.StartDateTime).date()
    slice_class.end_date = make_utc(mbo_class.EndDateTime).date()
    slice_class.start_time = make_utc(mbo_class.StartDateTime).time()
    slice_class.end_time = make_utc(mbo_class.EndDateTime).time()
    slice_class.mbolocation = mbolocation
    slice_class.is_active = mbo_class.Active
    if hasattr(mbo_class.ClassDescription, 'Level'):
        slice_class.level = mbo_class.ClassDescription.Level.Name

    slice_schedule = Schedule.objects.get_schedule_by_mbo_schedule_id_and_studio(mbo_class.ClassScheduleID, studio.id)
    # TODO :create schedule if it is not exist
    if slice_schedule:
        slice_class.schedule = slice_schedule
    if mbo_class.ClassDescription.Program:
        program = Program.objects.get_program_by_mbo_program_id_and_studio(mbo_class.ClassDescription.Program.ID, studio.id)
        slice_class.program = program


def map_values_from_mbo_session_type_to_slice_session_type(mbo_session_type, mbo_site_id):
    session_type = SessionType()
    session_type.name = mbo_session_type.Name
    session_type.mbo_session_type_id = mbo_session_type.ID
    session_type.mbo_site_id = mbo_site_id
    session_type.program_id = mbo_session_type.ProgramID
    session_type.num_deducted = mbo_session_type.NumDeducted
    return session_type


def update_values_from_mbo_class_to_slice_class(mbo_class, slice_class):
    slice_class.name = mbo_class.ClassDescription.Name

    if mbo_class.ClassDescription.Description:
        slice_class.description = strip_tags(mbo_class.ClassDescription.Description)

    slice_class.is_cancelled = mbo_class.IsCanceled
    slice_class.is_active = mbo_class.Active


def map_values_from_mbo_program_to_program(mbo_program):
    program = Program()
    program.mbo_program_id = mbo_program.ID
    program.schedule_type = mbo_program.ScheduleType
    program.cancel_off_set = mbo_program.CancelOffset
    return program
