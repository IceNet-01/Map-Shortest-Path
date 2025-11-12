# Usage Examples

This document provides practical examples of using the Global Shortest Path Calculator.

## Basic Great Circle Examples

### Simple Distance Calculation
```bash
# New York to London - coordinates
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278
```

**Output:**
```
======================================================================
GREAT CIRCLE DISTANCE (As The Crow Flies)
======================================================================

Starting Point: Point A: 40.7128°N, 74.0060°W
Ending Point:   Point B: 51.5074°N, 0.1278°W

Distance: 5570.22 kilometers
Initial Bearing: 51.2° (NE)

======================================================================
```

### Distance in Miles
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --unit mi
```

### Distance in Nautical Miles
```bash
# Useful for aviation and maritime applications
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 --unit nm
```

### With Named Points
```bash
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 \
  --name1 "New York, USA" \
  --name2 "London, UK"
```

### With Waypoints
```bash
# Generate 5 intermediate waypoints along the great circle path
python3 shortest_path.py 40.7128 -74.0060 51.5074 -0.1278 \
  --waypoints 5 \
  --unit mi \
  --name1 "New York" \
  --name2 "London"
```

## Road Routing Examples

### Driving Directions Between Addresses
```bash
# Simple driving route
python3 shortest_path.py --mode road --address \
  "Times Square, New York, NY" \
  "Central Park, New York, NY"
```

### With Turn-by-Turn Directions
```bash
python3 shortest_path.py --mode road --address \
  "Empire State Building, NYC" \
  "Statue of Liberty, NYC" \
  --directions
```

### Cycling Route
```bash
python3 shortest_path.py --mode road \
  --transport cycling \
  --address "Golden Gate Bridge, San Francisco" "Fisherman's Wharf, San Francisco" \
  --directions
```

### Walking Route
```bash
python3 shortest_path.py --mode road \
  --transport walking \
  --address "Boston Common, Boston" "Fenway Park, Boston" \
  --directions
```

### Road Route with Coordinates
```bash
# When you already have exact coordinates
python3 shortest_path.py --mode road 40.7128 -74.0060 40.7589 -73.9851
```

## Comparison Mode

### Compare Great Circle vs Road Distance
```bash
# See how much longer the road route is vs straight line
python3 shortest_path.py --mode both --address \
  "San Francisco, CA" \
  "Los Angeles, CA"
```

**Example Output:**
```
======================================================================
ROAD ROUTE SUMMARY
======================================================================

Total Distance: 617.50 km
Estimated Time: 5h 45m

Number of Steps: 47

======================================================================

======================================================================
GREAT CIRCLE DISTANCE (As The Crow Flies)
======================================================================

Starting Point: San Francisco, California, USA: 37.7749°N, 122.4194°W
Ending Point:   Los Angeles, California, USA: 34.0522°N, 118.2437°W

Distance: 559.12 km
Initial Bearing: 132.5° (SE)

======================================================================

======================================================================
COMPARISON
======================================================================

Great Circle (straight line): 559.12 km
Road Route (driving): 617.50 km
Difference: 58.38 km (10.4% longer)

Estimated travel time: 5h 45m

======================================================================
```

### Compare Cycling Route
```bash
python3 shortest_path.py --mode both \
  --transport cycling \
  --address "Seattle, WA" "Portland, OR"
```

## Advanced Use Cases

### Long-Distance Flight Planning
```bash
# Trans-Pacific route
python3 shortest_path.py \
  -33.8688 151.2093 \
  34.0522 -118.2437 \
  --unit nm \
  --waypoints 10 \
  --name1 "Sydney, Australia" \
  --name2 "Los Angeles, USA"
```

### Maritime Navigation
```bash
# Ocean crossing
python3 shortest_path.py \
  51.5074 -0.1278 \
  40.7128 -74.0060 \
  --unit nm \
  --waypoints 5 \
  --name1 "London" \
  --name2 "New York"
```

### Road Trip Planning
```bash
# Cross-country road trip with full directions
python3 shortest_path.py --mode both \
  --transport driving \
  --address "New York, NY" "Los Angeles, CA" \
  --unit mi \
  --directions
```

### Urban Commute Analysis
```bash
# Compare walking vs cycling for a commute
echo "Walking route:"
python3 shortest_path.py --mode road \
  --transport walking \
  --address "Times Square, NYC" "Wall Street, NYC"

echo -e "\nCycling route:"
python3 shortest_path.py --mode road \
  --transport cycling \
  --address "Times Square, NYC" "Wall Street, NYC"
```

## Tips & Best Practices

### For Great Circle Mode
- Use coordinates for precise locations
- Use nautical miles (`--unit nm`) for aviation/maritime
- Generate waypoints for long distances to see the curved path
- Remember: this is "as the crow flies", not actual travel distance

### For Road Routing Mode
- Be specific with addresses (include city and state/country)
- Use `--directions` flag for turn-by-turn navigation
- Choose appropriate transport mode:
  - `driving`: Uses highways, fastest routes
  - `cycling`: Prefers bike paths, avoids highways
  - `walking`: Uses sidewalks and pedestrian paths
- Road routing requires internet connectivity
- Public OSRM server may occasionally be unavailable

### For Comparison Mode
- Great for understanding route efficiency
- Shows percentage difference between straight-line and road distance
- Useful for planning whether a detour is worthwhile

## Troubleshooting

### "Could not geocode address"
- Make the address more specific
- Include city, state/province, country
- Try using coordinates instead
- Check your internet connection

### "Routing request error: 503 Service Unavailable"
- The public OSRM server is temporarily unavailable
- Try again in a few moments
- For production use, consider self-hosting OSRM
- Use great-circle mode as a fallback

### "Failed to calculate road route"
- Route may be too long (international ocean crossings won't work)
- Try coordinates that are connected by roads
- Ensure both points are in areas with road coverage

## Scripting Examples

### Batch Processing Multiple Routes
```bash
#!/bin/bash
# Calculate distances for multiple city pairs

cities=(
  "40.7128,-74.0060,New York"
  "34.0522,-118.2437,Los Angeles"
  "41.8781,-87.6298,Chicago"
  "29.7604,-95.3698,Houston"
)

for i in "${!cities[@]}"; do
  for j in "${!cities[@]}"; do
    if [ $i -lt $j ]; then
      IFS=',' read -r lat1 lon1 name1 <<< "${cities[$i]}"
      IFS=',' read -r lat2 lon2 name2 <<< "${cities[$j]}"

      echo "=== $name1 to $name2 ==="
      python3 shortest_path.py $lat1 $lon1 $lat2 $lon2 \
        --name1 "$name1" --name2 "$name2" --unit mi | grep "Distance:"
      echo
    fi
  done
done
```

### Save Route to File
```bash
# Save detailed route information
python3 shortest_path.py --mode road \
  --address "San Francisco, CA" "Sacramento, CA" \
  --directions > route_sf_to_sac.txt
```

## Integration Examples

### Python Script Integration
```python
import subprocess
import json

def get_distance(lat1, lon1, lat2, lon2):
    """Get great circle distance between two points."""
    result = subprocess.run([
        'python3', 'shortest_path.py',
        str(lat1), str(lon1), str(lat2), str(lon2)
    ], capture_output=True, text=True)

    # Parse output to extract distance
    for line in result.stdout.split('\n'):
        if 'Distance:' in line:
            distance = float(line.split()[1])
            return distance
    return None

# Example usage
dist = get_distance(40.7128, -74.0060, 51.5074, -0.1278)
print(f"Distance: {dist} km")
```

### Shell Function
```bash
# Add to ~/.bashrc or ~/.zshrc
distance() {
  python3 ~/Map-Shortest-Path/shortest_path.py "$@"
}

# Usage: distance 40.7128 -74.0060 51.5074 -0.1278
```
