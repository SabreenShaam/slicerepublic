from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


def get_nearest_rail_station(lat, lng):
    url = 'https://api.tfl.gov.uk/StopPoint'
    payload = {'lat': lat,
               'lon': lng,
               'stopTypes': 'NaptanMetroStation, NaptanRailStation',
               'radius': 1500,
               'useStopPointHierarchy': False,
               'modes': 'tube, dlr, national-rail, overground, tflrail',
               'returnLines': 'False',
               'app_id': settings.TFL_APP_ID,
               'app_key': settings.TFL_APP_KEY
               }
    response = requests.get(url, params=payload)
    data = response.json()
    if response.status_code == requests.codes.ok:
        return data
    logger.error(data['message'])
    return None
