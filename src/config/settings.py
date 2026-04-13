class Config:
    # Connection parameters
    DRONE_IP = "192.168.1.1"
    DRONE_PORT = 14550

    # UI settings
    WINDOW_TITLE = "Drone Ground Control Station"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 750

    # Telemetry update interval in milliseconds
    TELEMETRY_UPDATE_INTERVAL = 1000

    #For Map
    MAP_TILE_SERVER = "https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
    GPS_ACTIVE = True 
    
    #Deafult map center (for GPS mode)
    HOME_LAT = 22.4977117 
    HOME_LON = 88.3721941
    DEFAULT_ZOOM = 18

    # Other settings can be added here as needed
