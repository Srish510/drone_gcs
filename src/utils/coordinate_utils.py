def to_degrees(radians):
    return radians * (180.0 / 3.141592653589793)

def to_radians(degrees):
    return degrees * (3.141592653589793 / 180.0)

def haversine(coord1, coord2):
    from math import radians, sin, cos, sqrt, atan2

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6371  # Radius of Earth in kilometers
    return radius * c

def midpoint(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    mid_lat = (lat1 + lat2) / 2
    mid_lon = (lon1 + lon2) / 2

    return (mid_lat, mid_lon)