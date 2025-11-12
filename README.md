# Global Shortest Path Calculator

A comprehensive Python program that calculates the shortest path between any two points using **two methods**:

1. **Great Circle Distance** - Theoretical shortest distance on Earth's surface (as the crow flies)
2. **Road Routing** - Actual driving/cycling/walking routes with turn-by-turn directions

## Overview

### Great Circle Mode
Calculates the theoretical shortest distance between two geographic coordinates using spherical geometry and the Haversine formula. This represents the path an airplane or bird would take.

### Road Routing Mode
Provides real-world driving, cycling, or walking directions using actual road networks. Includes turn-by-turn navigation, distance, and estimated travel time.

## Features

### Great Circle Features
- **Haversine Formula**: Accurate spherical distance computation
- **Multiple Units**: Kilometers, miles, and nautical miles
- **Initial Bearing**: Compass direction to travel
- **Waypoint Generation**: Intermediate points along the optimal great circle path

### Road Routing Features
- **Address Geocoding**: Convert addresses to coordinates automatically
- **Multiple Transport Modes**: Driving, cycling, or walking
- **Turn-by-Turn Directions**: Detailed navigation instructions
- **Distance & Duration**: Actual road distance and estimated travel time
- **Real Road Networks**: Uses OpenStreetMap data via OSRM

### Additional Features
- **Comparison Mode**: Compare great circle vs actual road distance
- **Flexible Input**: Accept coordinates or street addresses
- **Command-line Interface**: Easy-to-use CLI with helpful examples

## Installation

No external dependencies required! Uses only Python standard library and free public APIs.

```bash
# Make the script executable
chmod +x shortest_path.py
```

## Usage

### Great Circle Mode (Default)

**Basic distance calculation:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278
```

**With waypoints and miles:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --unit mi --waypoints 3
```

**Named points:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --name1 "New York" --name2 "London"
```

### Road Routing Mode

**Driving directions between addresses:**
```bash
python3 shortest_path.py --mode road --address "Times Square, New York, NY" "Statue of Liberty, New York, NY"
```

**With turn-by-turn directions:**
```bash
python3 shortest_path.py --mode road --address "Central Park, NYC" "Empire State Building, NYC" --directions
```

**Cycling route:**
```bash
python3 shortest_path.py --mode road --transport cycling --address "Golden Gate Bridge, SF" "Fisherman's Wharf, SF" --directions
```

**Walking route between coordinates:**
```bash
python3 shortest_path.py --mode road --transport walking 40.7128 -74.0060 40.7589 -73.9851 --directions
```

### Comparison Mode

**Compare straight-line vs road distance:**
```bash
python3 shortest_path.py --mode both --address "San Francisco, CA" "Los Angeles, CA"
```

**Compare for a cycling trip:**
```bash
python3 shortest_path.py --mode both --transport cycling --address "Seattle, WA" "Portland, OR"
```

**Sydney to Los Angeles:**
```bash
python3 shortest_path.py -33.8688 151.2093 34.0522 -118.2437 --unit nm --waypoints 5
```

### Command-line Options

#### Routing Mode
- `--mode {great-circle,road,both}`: Choose routing method (default: great-circle)
  - `great-circle`: Calculate theoretical shortest distance on globe
  - `road`: Calculate actual road route with directions
  - `both`: Show both and compare

#### Input Format
- `--address`: Interpret inputs as addresses instead of coordinates
- Coordinates: `lat1 lon1 lat2 lon2` (four numeric values)
- Addresses: `--address "Start Address" "End Address"` (two quoted strings)

#### Transport Mode (Road Routing)
- `--transport {driving,cycling,walking}`: Transport mode for road routing (default: driving)

#### Great Circle Options
- `--unit {km,mi,nm}`: Unit of measurement (default: km)
- `--waypoints N`: Generate N intermediate waypoints along great circle
- `--name1 NAME`: Name for the starting point
- `--name2 NAME`: Name for the ending point

#### Road Routing Options
- `--directions`: Show detailed turn-by-turn directions

## Technical Details: How It Works

### The Great Circle Problem

When traveling between two points on Earth, the shortest path is **not** a straight line on a flat map. Because Earth is approximately spherical, the shortest path follows a **great circle** — a circle on the sphere's surface whose center coincides with the center of the sphere.

Think of it this way: if you stretch a string tightly between two points on a globe, the string follows a great circle path.

### 1. The Haversine Formula

The Haversine formula calculates the great circle distance between two points specified by latitude and longitude coordinates.

#### Mathematical Formula

Given two points with coordinates (φ₁, λ₁) and (φ₂, λ₂):

```
a = sin²(Δφ/2) + cos(φ₁) · cos(φ₂) · sin²(Δλ/2)
c = 2 · atan2(√a, √(1−a))
d = R · c
```

Where:
- φ = latitude (in radians)
- λ = longitude (in radians)
- Δφ = φ₂ - φ₁ (difference in latitude)
- Δλ = λ₂ - λ₁ (difference in longitude)
- R = Earth's radius (6,371 km, 3,959 mi, or 3,440 nm)
- d = distance between the two points

#### Why Haversine?

The Haversine formula is preferred over simpler formulas because:
1. **Numerical stability**: Avoids errors when calculating distances between close points
2. **Accuracy**: Works well for both short and long distances
3. **No singularities**: Unlike some formulas, it doesn't break down at the poles or equator

#### Implementation Details

```python
def haversine_distance(point1, point2, unit="km"):
    # Convert degrees to radians
    lat1_rad = math.radians(point1.lat)
    lon1_rad = math.radians(point1.lon)
    lat2_rad = math.radians(point2.lat)
    lon2_rad = math.radians(point2.lon)

    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Multiply by Earth's radius
    return radius * c
```

The formula uses the **haversine function**: hav(θ) = sin²(θ/2), which is particularly stable for small angles.

### 2. Initial Bearing Calculation

The initial bearing (also called forward azimuth) tells you which compass direction to start traveling from point A to reach point B along the great circle.

#### Mathematical Formula

```
θ = atan2(sin(Δλ) · cos(φ₂), cos(φ₁) · sin(φ₂) − sin(φ₁) · cos(φ₂) · cos(Δλ))
```

Where θ is the initial bearing in radians, converted to degrees (0-360°).

#### Important Note

The bearing along a great circle path is **not constant** (except when traveling due north/south or along the equator). This is why航海 navigation requires continuous course corrections or waypoint navigation.

### 3. Intermediate Waypoint Calculation

To generate waypoints along the great circle path, we use **spherical linear interpolation** (slerp).

#### Mathematical Formula

For a point at fraction `f` (0 ≤ f ≤ 1) along the path:

```
A = sin((1−f) · d) / sin(d)
B = sin(f · d) / sin(d)

x = A · cos(φ₁) · cos(λ₁) + B · cos(φ₂) · cos(λ₂)
y = A · cos(φ₁) · sin(λ₁) + B · cos(φ₂) · sin(λ₂)
z = A · sin(φ₁) + B · sin(φ₂)

φᵢ = atan2(z, √(x² + y²))
λᵢ = atan2(y, x)
```

Where:
- d = angular distance between the two points (in radians)
- f = fraction of the distance (0 = start, 1 = end, 0.5 = midpoint)
- (φᵢ, λᵢ) = coordinates of the intermediate point

#### How It Works

1. **Convert to 3D Cartesian**: Transform latitude/longitude into 3D unit vectors on a sphere
2. **Interpolate**: Use weighted combination based on the fraction
3. **Convert back**: Transform the 3D vector back to latitude/longitude

This ensures the waypoints lie exactly on the great circle path, not on a rhumb line or straight line on a flat projection.

### 4. Why Not Simple Linear Interpolation?

Simple linear interpolation of latitude and longitude coordinates would give you points that do **not** lie on the great circle path. On a 2D map they'd look reasonable, but on a sphere, you'd be traveling a longer route!

**Example:**
- Linear interpolation between (0°, 0°) and (0°, 180°) might pass through (0°, 90°)
- But the shortest path between these points goes over one of the poles!

### Coordinate System

- **Latitude**: -90° (South Pole) to +90° (North Pole)
- **Longitude**: -180° (West) to +180° (East)
- **Positive**: North and East
- **Negative**: South and West

### Earth Model

The program treats Earth as a perfect sphere with radius:
- 6,371 km (mean radius)
- 3,959 miles
- 3,440 nautical miles

**Note**: In reality, Earth is an oblate spheroid (slightly flattened at the poles). For most applications, the spherical model provides sufficient accuracy (within 0.5%). For survey-grade accuracy, use the Vincenty formula with the WGS84 ellipsoid model.

### Accuracy Considerations

**Haversine accuracy:**
- **Excellent** for distances < 10,000 km
- **Good** for distances up to ~20,000 km (half Earth's circumference)
- Small rounding errors possible for antipodal points (exactly opposite sides of Earth)

**Error sources:**
1. Earth is not a perfect sphere (~0.3% error from ellipsoid shape)
2. Terrain elevation not considered
3. Floating-point arithmetic (~10⁻¹⁵ relative error)

For most practical purposes, these errors are negligible.

---

## Road Routing: Technical Implementation

### Architecture Overview

The road routing system consists of three main components:

1. **Geocoding Service** (Nominatim)
2. **Routing Engine** (OSRM)
3. **Route Processing** (Local)

### 1. Geocoding with Nominatim

**Nominatim** is OpenStreetMap's geocoding service that converts addresses to geographic coordinates.

#### How It Works

```
Address String → HTTP Request → Nominatim API → JSON Response → Coordinates
```

**Example:**
- Input: `"Empire State Building, New York"`
- Output: `(40.7484, -73.9857, "Empire State Building, 350 5th Avenue, NYC...")`

#### Technical Details

- **API Endpoint**: `https://nominatim.openstreetmap.org/search`
- **Rate Limiting**: Maximum 1 request per second (enforced by the program)
- **No API Key Required**: Free to use with proper attribution
- **Data Source**: OpenStreetMap crowd-sourced data

#### Request Format

```
GET https://nominatim.openstreetmap.org/search?
  q=Empire+State+Building,+New+York
  &format=json
  &limit=1
  &addressdetails=1
```

#### Implementation Notes

The program:
1. URL-encodes the address
2. Adds required `User-Agent` header
3. Enforces rate limiting with `time.sleep()`
4. Parses JSON to extract latitude/longitude
5. Returns display name for user-friendly output

### 2. Road Routing with OSRM

**OSRM** (Open Source Routing Machine) is a high-performance routing engine using real road network data.

#### How It Works

```
Start Coords + End Coords → OSRM API → Route Geometry + Instructions → Formatted Directions
```

#### Routing Profiles

OSRM supports three transport modes, each with different constraints:

| Profile | Road Types | Speed Assumptions | Turn Restrictions |
|---------|-----------|-------------------|-------------------|
| **Car** | All drivable roads | Highway speeds | Yes (one-way, no left turn, etc.) |
| **Bike** | Bike lanes, roads, paths | ~15-20 km/h | Limited |
| **Foot** | Sidewalks, paths, roads | ~5 km/h | None (can go any direction) |

#### API Request

```
GET https://router.project-osrm.org/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}?
  steps=true
  &geometries=geojson
  &overview=full
```

**Important**: OSRM uses `longitude,latitude` order (NOT `latitude,longitude`)!

#### Response Structure

```json
{
  "code": "Ok",
  "routes": [{
    "distance": 5234.6,        // meters
    "duration": 623.4,         // seconds
    "geometry": {
      "coordinates": [[lon1,lat1], [lon2,lat2], ...]
    },
    "legs": [{
      "steps": [{
        "distance": 245.3,
        "duration": 34.2,
        "name": "5th Avenue",
        "maneuver": {
          "type": "turn",
          "modifier": "left",
          "location": [lon, lat]
        }
      }, ...]
    }]
  }]
}
```

### 3. Route Processing

The program processes OSRM's response to create user-friendly output:

#### Step Interpretation

The program converts OSRM maneuver types into natural language:

| Maneuver Type | Modifier | Instruction |
|--------------|----------|-------------|
| `depart` | `north` | "Head north on Main Street" |
| `turn` | `left` | "Turn left onto 5th Avenue" |
| `turn` | `right` | "Turn right onto Broadway" |
| `merge` | `slight left` | "Merge slight left" |
| `roundabout` | - | "Take roundabout onto Park Ave" |
| `arrive` | - | "Arrive at destination" |

#### Distance Formatting

Smart distance formatting based on magnitude:

- **Metric**: < 100m → meters; ≥ 100m → kilometers
- **Imperial**: < 528 feet (0.1 mi) → feet; ≥ 528 feet → miles

#### Duration Formatting

- < 60 seconds: "45s"
- 1-60 minutes: "23m 15s"
- > 60 minutes: "2h 45m"

### Data Flow Example

**User Input:**
```bash
python3 shortest_path.py --mode road --address "Boston, MA" "New York, NY" --directions
```

**Processing Steps:**

1. **Geocode Start**
   - Query: "Boston, MA"
   - Result: `(42.3601, -71.0589, "Boston, Massachusetts, USA")`

2. **Geocode End**
   - Query: "New York, NY"
   - Result: `(40.7128, -74.0060, "New York, New York, USA")`

3. **Route Request**
   - URL: `https://router.project-osrm.org/route/v1/car/-71.0589,42.3601;-74.0060,40.7128?steps=true...`
   - Response: Route with ~50 steps, 346 km, 3.5 hours

4. **Process & Display**
   - Parse maneuvers into instructions
   - Format distances and durations
   - Display summary and turn-by-turn directions

### Why Free APIs?

#### Nominatim (OpenStreetMap)
- **Free**: No API keys, no quotas for reasonable use
- **Open Data**: Crowd-sourced, constantly updated
- **Global Coverage**: Addresses worldwide
- **Limitation**: 1 request/second rate limit

#### OSRM Public Server
- **Free**: No authentication required
- **Fast**: Optimized C++ implementation
- **Data**: Based on OpenStreetMap road network
- **Limitation**: Public server for light use only
- **Production Alternative**: Self-host OSRM server

### Network Topology: How Routing Works

Road routing uses **graph algorithms** on a network where:

- **Nodes** = Intersections, endpoints
- **Edges** = Road segments with weights (distance, time, restrictions)

#### Dijkstra's Algorithm (Simplified)

OSRM uses optimized variants of Dijkstra's algorithm with preprocessing:

```
1. Start at source node
2. Explore neighboring nodes, tracking cumulative distance
3. Always expand the closest unvisited node next
4. Continue until reaching destination
5. Backtrack to reconstruct the path
```

**Optimizations used by OSRM:**
- **Contraction Hierarchies**: Preprocess road network for faster queries
- **Bidirectional Search**: Search from both start and end simultaneously
- **Heuristics**: A* algorithm with geographic distance estimation

### Accuracy Considerations

#### Geocoding Accuracy
- Depends on address specificity
- City-level: ~center of city (could be kilometers off)
- Street address: Usually within 10-50 meters
- Specific POI: Usually very accurate

#### Routing Accuracy
- **Distance**: Typically accurate within 1-2%
- **Duration**: Estimates based on speed limits and road types
  - Does NOT account for: Traffic, weather, construction, driver behavior
  - Real-world times can vary ±30% or more

#### Real-World Factors Not Considered
- Live traffic conditions
- Road closures and construction
- Traffic signals and stop signs
- Weather conditions
- Driver skill and vehicle type
- Parking and final approach

## Real-World Applications

### Great Circle Applications
1. **Aviation**: Flight path planning and fuel calculation
2. **Maritime**: Ship navigation and route optimization
3. **Telecommunications**: Satellite coverage and signal path calculation
4. **Research**: Studying global phenomena (migration patterns, climate, etc.)
5. **Logistics**: International shipping distance estimates

### Road Routing Applications
1. **Trip Planning**: Vacation route planning with distance and time estimates
2. **Delivery Services**: Route optimization for last-mile delivery
3. **Emergency Response**: Calculating actual travel time for ambulances, fire trucks
4. **Urban Planning**: Analyzing accessibility and commute times
5. **Real Estate**: Commute distance calculations from properties
6. **Cycling & Hiking**: Planning routes for outdoor activities
7. **Logistics**: Local and regional delivery route planning
8. **Ride Sharing**: Estimating pickup times and routes

## Mathematical Background: Why Great Circles?

### Geodesics on a Sphere

In differential geometry, a **geodesic** is the shortest path between two points on a curved surface. On a flat plane, geodesics are straight lines. On a sphere, geodesics are segments of great circles.

### Proof Sketch

Consider any path on a sphere between two points. If the path deviates from the great circle, you can "straighten" it by moving it closer to the great circle, reducing its length. The only path that cannot be shortened further is the great circle itself.

### Alternative: Rhumb Lines

A **rhumb line** (or loxodrome) is a path of constant bearing — easier to navigate but longer than the great circle. Ships and aircraft often use rhumb lines for short distances because they're simpler to follow, but switch to great circle routes (broken into waypoints) for long distances.

## Performance

- **Time Complexity**: O(1) for distance calculation, O(n) for n waypoints
- **Space Complexity**: O(n) for storing n waypoints
- **Typical Execution Time**: < 1ms for single calculation

## License

This is free and open-source software.

## Further Reading

### Great Circle & Geodesy
- [Haversine Formula - Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
- [Great Circle - Wikipedia](https://en.wikipedia.org/wiki/Great_circle)
- [Aviation Formulary - Ed Williams](http://edwilliams.org/avform.htm)
- [Movable Type Scripts - Geodesy Functions](https://www.movable-type.co.uk/scripts/latlong.html)

### Road Routing & Geocoding
- [OSRM Documentation](http://project-osrm.org/)
- [Nominatim API Documentation](https://nominatim.org/release-docs/latest/api/Overview/)
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/)
- [Dijkstra's Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Contraction Hierarchies - Wikipedia](https://en.wikipedia.org/wiki/Contraction_hierarchies)

## Contributing

Contributions are welcome! Some ideas for enhancements:

### Great Circle Enhancements
- [ ] Add support for the more accurate Vincenty formula
- [ ] Implement rhumb line calculations for comparison
- [ ] Add antipodal point detection and handling
- [ ] Include elevation data for actual surface distance

### Road Routing Enhancements
- [ ] Support for multiple waypoints (A → B → C → D routing)
- [ ] Alternative route suggestions
- [ ] Traffic data integration
- [ ] Avoid tolls/highways options
- [ ] Export routes to GPX/KML format
- [ ] Route optimization (traveling salesman problem)
- [ ] Batch geocoding from CSV files

### Visualization & UI
- [ ] Add interactive map visualization with folium or leaflet
- [ ] Create a web interface with Flask/FastAPI
- [ ] Generate route elevation profiles
- [ ] Export routes to Google Maps / Apple Maps
- [ ] Mobile-friendly responsive design

### Performance & Features
- [ ] Caching for geocoding results
- [ ] Offline mode with local OSM data
- [ ] Support for custom OSRM server endpoints
- [ ] Parallel route calculation for comparison
- [ ] Integration with public transit APIs

## Contact

For questions or issues, please open an issue on the GitHub repository.
