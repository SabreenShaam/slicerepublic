from django.db import connection


def get_studios_with_settings():
    cursor = connection.cursor()
    cursor.execute("SELECT vs.id, vs.name, vss.room_location_enabled FROM venues_studio as vs LEFT JOIN venues_studiosettings as vss ON (vs.id = vss.studio_id)")
    rows = cursor.fetchall()
    return rows
