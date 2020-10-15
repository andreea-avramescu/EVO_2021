# Two different distance functions
import numpy as np

# haversine formula 
def haversine(A_lon,A_lat,B_lon,B_lat):
    A_lon,A_lat,B_lon,B_lat = map(np.radians, [A_lon,A_lat,B_lon,B_lat])

    dlon = B_lon - A_lon
    dlat = B_lat - A_lat

    a = np.sin(dlat/2.0)**2 + np.cos(A_lat) * np.cos(B_lat) * np.sin(dlon/2.0)**2

    c = 2.0 * 6371.0  # Replace 6371 with 3958.756 if you want the answer in miles.

    return c * np.arcsin(np.sqrt(a))

    # L2 distance
def L2_distance(A_lon,A_lat,B_lon,B_lat):
    xDis = np.absolute(A_lon - B_lon)
    yDis = np.absolute(A_lat - B_lat)
    distance = np.sqrt(np.square(xDis) + np.square(yDis))
    return distance
