import geopy

from lib.logging import logger

def geo_reverse(geolocator, lat, lon):
    location = []
    try:
        location = geolocator.reverse('%s, %s' % (lat, lon), timeout=10)
    except geopy.exc.ConfigurationError as e:
        logger.error("something wrong in the geo configuration")
        logger.error("{}".format(e))
    except geopy.exc.GeocoderAuthenticationFailure as e:
        logger.error("Authentication Failure with the geolocation service")
        logger.error("{}".format(e))
    except geopy.exc.GeocoderServiceError as e:
        logger.error("something wrong with the geolocation service")
        logger.error("{}".format(e))
    finally:
        if location:
            if geolocator.__class__.__name__ == 'Nominatim':
                return [location.raw['address'].get('road', '??'), location.raw['address'].get('house_number', '??'),
                        location.raw['address'].get('postcode', '??'), location.raw['address'].get('town', '??')]
            elif geolocator.__class__.__name__ == 'GoogleV3':
                detail = {}
                for item in location.raw.get('address_components'):
                    for category in item['types']:
                        detail[category] = item['short_name']
                return [detail.get('route', '??'), detail.get('street_number', '??'), detail.get('postal_code', '??'),
                        detail.get('locality', detail.get('postal_town', '??'))]
        else:
            return ["??", "??", "??", "??"]


