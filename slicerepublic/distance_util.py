from geopy.distance import vincenty
from django.conf import settings


def is_inside_radius(lat1, lng1, lat2, lng2):
    point1 = (lat1, lng1)
    point2 = (lat2, lng2)

    distance = vincenty(point1, point2).m
    if distance < settings.GEO_SIGN_IN_RADIUS:
        return True
    return False
