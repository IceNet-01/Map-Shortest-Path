# Global Shortest Path Calculator

A Python program that calculates the shortest path between any two points on Earth's surface using spherical geometry and the great circle distance formula.

## Overview

This program finds the shortest distance between two geographic coordinates (latitude/longitude pairs) by calculating the **great circle distance** — the shortest path between two points on the surface of a sphere.

## Features

- **Great Circle Distance Calculation**: Uses the Haversine formula for accurate distance computation
- **Multiple Units**: Support for kilometers, miles, and nautical miles
- **Initial Bearing**: Calculates the compass direction to travel
- **Waypoint Generation**: Creates intermediate points along the optimal path
- **Command-line Interface**: Easy-to-use CLI with helpful examples

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Make the script executable
chmod +x shortest_path.py
```

## Usage

### Basic Usage

```bash
python3 shortest_path.py <lat1> <lon1> <lat2> <lon2>
```

### Examples

**New York to London:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278
```

**Distance in miles with waypoints:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --unit mi --waypoints 3
```

**Named points:**
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --name1 "New York" --name2 "London"
```

**Sydney to Los Angeles:**
```bash
python3 shortest_path.py -33.8688 151.2093 34.0522 -118.2437 --unit nm --waypoints 5
```

### Command-line Options

- `lat1, lon1`: Latitude and longitude of the starting point
- `lat2, lon2`: Latitude and longitude of the ending point
- `--unit`: Unit of measurement (`km`, `mi`, or `nm`)
- `--waypoints N`: Generate N intermediate waypoints along the path
- `--name1 NAME`: Name for the starting point
- `--name2 NAME`: Name for the ending point

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

## Real-World Applications

1. **Aviation**: Flight path planning and fuel calculation
2. **Maritime**: Ship navigation and route optimization
3. **Logistics**: Distance calculations for global shipping
4. **Emergency Services**: Calculating response ranges
5. **Telecommunications**: Satellite coverage and signal path calculation
6. **Research**: Studying global phenomena (migration patterns, climate, etc.)

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

- [Haversine Formula - Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
- [Great Circle - Wikipedia](https://en.wikipedia.org/wiki/Great_circle)
- [Aviation Formulary - Ed Williams](http://edwilliams.org/avform.htm)
- [Movable Type Scripts - Geodesy Functions](https://www.movable-type.co.uk/scripts/latlong.html)

## Contributing

Contributions are welcome! Some ideas for enhancements:

- [ ] Add support for the more accurate Vincenty formula
- [ ] Implement rhumb line calculations for comparison
- [ ] Add visualization with matplotlib or folium
- [ ] Create a web interface
- [ ] Support for reading coordinates from files
- [ ] Add antipodal point detection and handling
- [ ] Include elevation data for actual surface distance

## Contact

For questions or issues, please open an issue on the GitHub repository.
