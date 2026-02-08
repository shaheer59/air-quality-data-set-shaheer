"""
Geographic Data and Coordinate Mapping for NYC Neighborhoods
"""

# Approximate centroids for NYC Neighborhoods and Community Districts (UHF/CD)
# Sources: NYC Open Data, Google Maps approximations
# Format: 'Geo Place Name': {'lat': latitude, 'lon': longitude}

NYC_COORDINATES = {
    # --- Manhattan ---
    'Chelsea-Village': {'lat': 40.7376, 'lon': -74.0015},
    'Greenwich Village and Soho (CD2)': {'lat': 40.7260, 'lon': -74.0000},
    'Greenwich Village - SoHo': {'lat': 40.7260, 'lon': -74.0000},
    'Union Square - Lower East Side': {'lat': 40.7250, 'lon': -73.9850},
    'Lower East Side and Chinatown (CD3)': {'lat': 40.7150, 'lon': -73.9900},
    'Chinatown': {'lat': 40.7150, 'lon': -73.9970},
    'Financial District (CD1)': {'lat': 40.7075, 'lon': -74.0113},
    'Lower Manhattan': {'lat': 40.7120, 'lon': -74.0080},
    'Clinton and Chelsea (CD4)': {'lat': 40.7550, 'lon': -73.9950},
    'Chelsea - Clinton': {'lat': 40.7550, 'lon': -73.9950},
    'Midtown (CD5)': {'lat': 40.7580, 'lon': -73.9855},
    'Stuyvesant Town and Turtle Bay (CD6)': {'lat': 40.7390, 'lon': -73.9750},
    'Gramercy Park - Murray Hill': {'lat': 40.7420, 'lon': -73.9800},
    'Upper West Side (CD7)': {'lat': 40.7870, 'lon': -73.9754},
    'Upper West Side': {'lat': 40.7870, 'lon': -73.9754},
    'Upper East Side (CD8)': {'lat': 40.7736, 'lon': -73.9566},
    'Upper East Side': {'lat': 40.7736, 'lon': -73.9566},
    'Upper East Side-Gramercy': {'lat': 40.7600, 'lon': -73.9650},
    'Morningside Heights and Hamilton Heights (CD9)': {'lat': 40.8150, 'lon': -73.9550},
    'Central Harlem - Morningside Heights': {'lat': 40.8100, 'lon': -73.9500},
    'Central Harlem (CD10)': {'lat': 40.8100, 'lon': -73.9450},
    'East Harlem (CD11)': {'lat': 40.7957, 'lon': -73.9389},
    'East Harlem': {'lat': 40.7957, 'lon': -73.9389},
    'Washington Heights and Inwood (CD12)': {'lat': 40.8500, 'lon': -73.9300},
    'Washington Heights': {'lat': 40.8417, 'lon': -73.9394},
    'Inwood': {'lat': 40.8677, 'lon': -73.9212},
    'Manhattan': {'lat': 40.7831, 'lon': -73.9712},

    # --- Bronx ---
    'Mott Haven and Melrose (CD1)': {'lat': 40.8100, 'lon': -73.9200},
    'Hunts Point and Longwood (CD2)': {'lat': 40.8200, 'lon': -73.8900},
    'Hunts Point - Mott Haven': {'lat': 40.8150, 'lon': -73.9000},
    'Morrisania and Crotona (CD3)': {'lat': 40.8300, 'lon': -73.9000},
    'Highbridge and Concourse (CD4)': {'lat': 40.8350, 'lon': -73.9200},
    'High Bridge - Morrisania': {'lat': 40.8350, 'lon': -73.9200},
    'Fordham and University Heights (CD5)': {'lat': 40.8600, 'lon': -73.9000},
    'Belmont and East Tremont (CD6)': {'lat': 40.8500, 'lon': -73.8900},
    'Kingsbridge Heights and Bedford (CD7)': {'lat': 40.8700, 'lon': -73.8950},
    'Riverdale and Fieldston (CD8)': {'lat': 40.8900, 'lon': -73.9000},
    'Kingsbridge - Riverdale': {'lat': 40.8800, 'lon': -73.9050},
    'Parkchester and Soundview (CD9)': {'lat': 40.8300, 'lon': -73.8600},
    'Throgs Neck and Co-op City (CD10)': {'lat': 40.8400, 'lon': -73.8200},
    'Morris Park and Bronxdale (CD11)': {'lat': 40.8500, 'lon': -73.8500},
    'Williamsbridge and Baychester (CD12)': {'lat': 40.8800, 'lon': -73.8500},
    'Northeast Bronx': {'lat': 40.8700, 'lon': -73.8400},
    'Fordham - Bronx Pk': {'lat': 40.8600, 'lon': -73.8800},
    'Pelham - Throgs Neck': {'lat': 40.8400, 'lon': -73.8100},
    'Crotona -Tremont': {'lat': 40.8400, 'lon': -73.8900},
    'South Bronx': {'lat': 40.8100, 'lon': -73.9100},
    'Bronx': {'lat': 40.8448, 'lon': -73.8648},

    # --- Brooklyn ---
    'Greenpoint and Williamsburg (CD1)': {'lat': 40.7200, 'lon': -73.9500},
    'Greenpoint': {'lat': 40.7300, 'lon': -73.9515},
    'Williamsburg - Bushwick': {'lat': 40.7100, 'lon': -73.9400},
    'Fort Greene and Brooklyn Heights (CD2)': {'lat': 40.6900, 'lon': -73.9750},
    'Downtown - Heights - Slope': {'lat': 40.6900, 'lon': -73.9900},
    'Bedford Stuyvesant (CD3)': {'lat': 40.6872, 'lon': -73.9418},
    'Bedford Stuyvesant - Crown Heights': {'lat': 40.6800, 'lon': -73.9400},
    'Bushwick (CD4)': {'lat': 40.6944, 'lon': -73.9213},
    'East New York and Starrett City (CD5)': {'lat': 40.6600, 'lon': -73.8900},
    'East New York': {'lat': 40.6667, 'lon': -73.8825},
    'Park Slope and Carroll Gardens (CD6)': {'lat': 40.6750, 'lon': -73.9850},
    'Sunset Park (CD7)': {'lat': 40.6450, 'lon': -74.0050},
    'Sunset Park': {'lat': 40.6450, 'lon': -74.0050},
    'Crown Heights and Prospect Heights (CD8)': {'lat': 40.6700, 'lon': -73.9500},
    'South Crown Heights and Lefferts Gardens (CD9)': {'lat': 40.6600, 'lon': -73.9500},
    'Bay Ridge and Dyker Heights (CD10)': {'lat': 40.6300, 'lon': -74.0200},
    'Bensonhurst - Bay Ridge': {'lat': 40.6200, 'lon': -74.0000},
    'Bensonhurst (CD11)': {'lat': 40.6100, 'lon': -73.9950},
    'Borough Park (CD12)': {'lat': 40.6350, 'lon': -73.9950},
    'Borough Park': {'lat': 40.6350, 'lon': -73.9950},
    'Coney Island (CD13)': {'lat': 40.5750, 'lon': -73.9800},
    'Coney Island - Sheepshead Bay': {'lat': 40.5750, 'lon': -73.9600},
    'Flatbush and Midwood (CD14)': {'lat': 40.6400, 'lon': -73.9600},
    'Sheepshead Bay (CD15)': {'lat': 40.5900, 'lon': -73.9500},
    'Brownsville (CD16)': {'lat': 40.6650, 'lon': -73.9100},
    'East Flatbush (CD17)': {'lat': 40.6500, 'lon': -73.9300},
    'East Flatbush - Flatbush': {'lat': 40.6500, 'lon': -73.9450},
    'Flatlands and Canarsie (CD18)': {'lat': 40.6300, 'lon': -73.9100},
    'Canarsie - Flatlands': {'lat': 40.6300, 'lon': -73.9000},
    'Brooklyn': {'lat': 40.6782, 'lon': -73.9442},

    # --- Queens ---
    'Long Island City and Astoria (CD1)': {'lat': 40.7600, 'lon': -73.9250},
    'Long Island City - Astoria': {'lat': 40.7600, 'lon': -73.9250},
    'Woodside and Sunnyside (CD2)': {'lat': 40.7450, 'lon': -73.9150},
    'West Queens': {'lat': 40.7450, 'lon': -73.9150},
    'Jackson Heights (CD3)': {'lat': 40.7557, 'lon': -73.8831},
    'Elmhurst and Corona (CD4)': {'lat': 40.7400, 'lon': -73.8700},
    'Ridgewood and Maspeth (CD5)': {'lat': 40.7100, 'lon': -73.9050},
    'Rego Park and Forest Hills (CD6)': {'lat': 40.7250, 'lon': -73.8550},
    'Ridgewood - Forest Hills': {'lat': 40.7150, 'lon': -73.8600},
    'Flushing and Whitestone (CD7)': {'lat': 40.7700, 'lon': -73.8200},
    'Flushing - Clearview': {'lat': 40.7650, 'lon': -73.8000},
    'Hillcrest and Fresh Meadows (CD8)': {'lat': 40.7300, 'lon': -73.7900},
    'Fresh Meadows': {'lat': 40.7400, 'lon': -73.7850},
    'Kew Gardens and Woodhaven (CD9)': {'lat': 40.7000, 'lon': -73.8400},
    'South Ozone Park and Howard Beach (CD10)': {'lat': 40.6700, 'lon': -73.8300},
    'Southwest Queens': {'lat': 40.6800, 'lon': -73.8400},
    'Bayside and Little Neck (CD11)': {'lat': 40.7650, 'lon': -73.7650},
    'Bayside - Little Neck': {'lat': 40.7650, 'lon': -73.7650},
    'Bayside Little Neck-Fresh Meadows': {'lat': 40.7550, 'lon': -73.7750},
    'Jamaica and Hollis (CD12)': {'lat': 40.7050, 'lon': -73.7900},
    'Jamaica': {'lat': 40.7027, 'lon': -73.7938},
    'Queens Village (CD13)': {'lat': 40.7250, 'lon': -73.7400},
    'Southeast Queens': {'lat': 40.7000, 'lon': -73.7600},
    'Rockaway and Broad Channel (CD14)': {'lat': 40.6000, 'lon': -73.8000},
    'Rockaways': {'lat': 40.5900, 'lon': -73.8000},
    'Queens': {'lat': 40.7282, 'lon': -73.7949},

    # --- Staten Island ---
    'St. George and Stapleton (CD1)': {'lat': 40.6350, 'lon': -74.0850},
    'Stapleton - St. George': {'lat': 40.6350, 'lon': -74.0850},
    'Northern SI': {'lat': 40.6300, 'lon': -74.1000},
    'Port Richmond': {'lat': 40.6334, 'lon': -74.1263},
    'South Beach and Willowbrook (CD2)': {'lat': 40.5900, 'lon': -74.1000},
    'South Beach - Tottenville': {'lat': 40.5500, 'lon': -74.1500},
    'Willowbrook': {'lat': 40.6031, 'lon': -74.1385},
    'Tottenville and Great Kills (CD3)': {'lat': 40.5400, 'lon': -74.1800},
    'Southern SI': {'lat': 40.5500, 'lon': -74.1800},
    'Staten Island': {'lat': 40.5795, 'lon': -74.1502},

    # --- Citywide ---
    'New York City': {'lat': 40.7128, 'lon': -74.0060},
}

def get_coordinates(place_name: str) -> dict:
    """Get latitude and longitude for a place name with fallback."""
    # 1. Direct match
    if place_name in NYC_COORDINATES:
        return NYC_COORDINATES[place_name]
    
    # 2. Heuristic matching (simple string containment)
    for key, coords in NYC_COORDINATES.items():
        if place_name.lower().strip() == key.lower().strip():
             return coords
        # Check if key is a significant substring of place_name
        if len(key) > 5 and key in place_name:
             return coords
             
    # 3. Default (NYC Center)
    return {'lat': 40.7128, 'lon': -74.0060}
