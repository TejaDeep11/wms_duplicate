from geopy.distance import great_circle

def calculate_distance(coords_1, coords_2):
    """
    Calculates the distance between two (lat, lon) points in meters.
    """
    if not coords_1 or not coords_2 or None in coords_1 or None in coords_2:
        return float('inf')
    
    return great_circle(coords_1, coords_2).meters