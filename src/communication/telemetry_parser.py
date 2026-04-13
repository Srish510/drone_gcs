import math

def parse_telemetry_data(data: dict) -> dict:

    parsed_data = {}

    parsed_data['altitude'] = data.get('altitude', 0)
    # parsed_data['latitude'] = data.get('latitude', 0.0)
    # parsed_data['longitude'] = data.get('longitude', 0.0)
    
    parsed_data['vx'] = data.get('vx', 0.0)
    parsed_data['vy'] = data.get('vy', 0.0)
    parsed_data['vz'] = data.get('vz', 0.0)
    parsed_data['speed'] = math.sqrt(parsed_data['vx']**2 + parsed_data['vy']**2 + parsed_data['vz']**2)
    parsed_data['battery'] = data.get('battery', 0)
    parsed_data['ax'] = data.get('ax', 0.0)
    parsed_data['ay'] = data.get('ay', 0.0)
    parsed_data['az'] = data.get('az', 0.0)
    parsed_data['roll'] = data.get('roll', 0.0)
    parsed_data['pitch'] = data.get('pitch', 0.0)
    parsed_data['yaw'] = data.get('yaw', 0.0)
    parsed_data['flight_mode'] = data.get('flight_mode', "UNKNOWN")
    parsed_data['armed'] = data.get('armed', False)
    parsed_data['lat'] = data.get('lat', 0.0)
    parsed_data['lon'] = data.get('lon', 0.0)
    parsed_data['north'] = data.get('north', 0.0)
    parsed_data['east'] = data.get('east', 0.0) 

    return parsed_data