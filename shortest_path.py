#!/usr/bin/env python3
"""
Global Shortest Path Calculator

This program calculates the shortest path between two geographic points
on Earth's surface using:
1. Great circle distance (Haversine formula) - straight line on globe
2. Road routing - actual driving/walking/cycling directions
"""

import math
import argparse
import sys
from typing import Tuple, List, Optional

try:
    from road_routing import (
        RoadRouter, format_route_summary, format_turn_by_turn,
        GeocodingService
    )
    ROAD_ROUTING_AVAILABLE = True
except ImportError:
    ROAD_ROUTING_AVAILABLE = False


class GeoPoint:
    """Represents a geographic point with latitude and longitude."""

    def __init__(self, latitude: float, longitude: float, name: str = ""):
        """
        Initialize a geographic point.

        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            name: Optional name for the point
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")

        self.lat = latitude
        self.lon = longitude
        self.name = name

    def __str__(self):
        name_str = f"{self.name}: " if self.name else ""
        lat_dir = "N" if self.lat >= 0 else "S"
        lon_dir = "E" if self.lon >= 0 else "W"
        return f"{name_str}{abs(self.lat):.4f}°{lat_dir}, {abs(self.lon):.4f}°{lon_dir}"


class ShortestPathCalculator:
    """Calculator for shortest paths on Earth's surface."""

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MI = 3959.0
    EARTH_RADIUS_NM = 3440.0  # Nautical miles

    @staticmethod
    def haversine_distance(point1: GeoPoint, point2: GeoPoint, unit: str = "km") -> float:
        """
        Calculate the great circle distance between two points using the Haversine formula.

        Args:
            point1: First geographic point
            point2: Second geographic point
            unit: Unit of measurement ("km", "mi", "nm")

        Returns:
            Distance in the specified unit
        """
        # Convert latitude and longitude to radians
        lat1_rad = math.radians(point1.lat)
        lon1_rad = math.radians(point1.lon)
        lat2_rad = math.radians(point2.lat)
        lon2_rad = math.radians(point2.lon)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Select Earth radius based on unit
        radius = {
            "km": ShortestPathCalculator.EARTH_RADIUS_KM,
            "mi": ShortestPathCalculator.EARTH_RADIUS_MI,
            "nm": ShortestPathCalculator.EARTH_RADIUS_NM
        }.get(unit.lower(), ShortestPathCalculator.EARTH_RADIUS_KM)

        return radius * c

    @staticmethod
    def initial_bearing(point1: GeoPoint, point2: GeoPoint) -> float:
        """
        Calculate the initial bearing (forward azimuth) from point1 to point2.

        Args:
            point1: Starting point
            point2: Ending point

        Returns:
            Initial bearing in degrees (0-360)
        """
        lat1_rad = math.radians(point1.lat)
        lat2_rad = math.radians(point2.lat)
        dlon_rad = math.radians(point2.lon - point1.lon)

        x = math.sin(dlon_rad) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad)

        initial_bearing = math.atan2(x, y)

        # Convert to degrees and normalize to 0-360
        return (math.degrees(initial_bearing) + 360) % 360

    @staticmethod
    def intermediate_point(point1: GeoPoint, point2: GeoPoint, fraction: float) -> GeoPoint:
        """
        Calculate an intermediate point along the great circle path.

        Args:
            point1: Starting point
            point2: Ending point
            fraction: Fraction of the distance (0.0 to 1.0)

        Returns:
            Intermediate point
        """
        lat1_rad = math.radians(point1.lat)
        lon1_rad = math.radians(point1.lon)
        lat2_rad = math.radians(point2.lat)
        lon2_rad = math.radians(point2.lon)

        # Angular distance
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        d = 2 * math.asin(math.sqrt(a))

        if d == 0:
            return GeoPoint(point1.lat, point1.lon)

        A = math.sin((1 - fraction) * d) / math.sin(d)
        B = math.sin(fraction * d) / math.sin(d)

        x = A * math.cos(lat1_rad) * math.cos(lon1_rad) + \
            B * math.cos(lat2_rad) * math.cos(lon2_rad)
        y = A * math.cos(lat1_rad) * math.sin(lon1_rad) + \
            B * math.cos(lat2_rad) * math.sin(lon2_rad)
        z = A * math.sin(lat1_rad) + B * math.sin(lat2_rad)

        lat = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
        lon = math.atan2(y, x)

        return GeoPoint(math.degrees(lat), math.degrees(lon))

    @staticmethod
    def generate_waypoints(point1: GeoPoint, point2: GeoPoint, num_waypoints: int = 5) -> List[GeoPoint]:
        """
        Generate waypoints along the great circle path.

        Args:
            point1: Starting point
            point2: Ending point
            num_waypoints: Number of intermediate waypoints (excluding start and end)

        Returns:
            List of waypoints including start and end points
        """
        waypoints = [point1]

        for i in range(1, num_waypoints + 1):
            fraction = i / (num_waypoints + 1)
            waypoint = ShortestPathCalculator.intermediate_point(point1, point2, fraction)
            waypoint.name = f"Waypoint {i}"
            waypoints.append(waypoint)

        waypoints.append(point2)
        return waypoints


def format_bearing(bearing: float) -> str:
    """Convert bearing to compass direction."""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(bearing / 22.5) % 16
    return f"{bearing:.1f}° ({directions[index]})"


def main():
    """Main program entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate the shortest path between two points using great circle or road routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Great circle distance from New York to London (coordinates)
  %(prog)s 40.7128 -74.0060 51.5074 -0.1278

  # Road route from addresses (driving directions)
  %(prog)s --mode road --address "Times Square, New York" "Trafalgar Square, London"

  # Cycling route between coordinates
  %(prog)s --mode road --transport cycling 40.7128 -74.0060 40.7589 -73.9851

  # Walking route with turn-by-turn directions
  %(prog)s --mode road --transport walking --address "Central Park, NYC" "Empire State Building, NYC" --directions

  # Great circle with waypoints in miles
  %(prog)s 40.7128 -74.0060 51.5074 -0.1278 --unit mi --waypoints 3

  # Compare both modes
  %(prog)s --mode both --address "San Francisco, CA" "Los Angeles, CA"
        """
    )

    # Input mode
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--address", action="store_true",
                           help="Interpret inputs as addresses instead of coordinates")

    # Routing mode
    parser.add_argument("--mode", choices=["great-circle", "road", "both"], default="great-circle",
                        help="Routing mode: great-circle (as crow flies), road (actual roads), or both")

    # Transport mode for road routing
    parser.add_argument("--transport", choices=["driving", "cycling", "walking"], default="driving",
                        help="Transport mode for road routing")

    # Position arguments - can be coordinates or addresses
    parser.add_argument("start", nargs="?", type=str,
                        help="Starting point (latitude or address if --address flag is used)")
    parser.add_argument("start_lon", nargs="?", type=str,
                        help="Starting longitude (not used with --address)")
    parser.add_argument("end", nargs="?", type=str,
                        help="Ending point (latitude or address if --address flag is used)")
    parser.add_argument("end_lon", nargs="?", type=str,
                        help="Ending longitude (not used with --address)")

    # Great circle options
    parser.add_argument("--unit", choices=["km", "mi", "nm"], default="km",
                        help="Unit of measurement (km=kilometers, mi=miles, nm=nautical miles)")
    parser.add_argument("--waypoints", type=int, default=0,
                        help="Number of intermediate waypoints for great circle route")
    parser.add_argument("--name1", type=str, default="",
                        help="Name for the first point")
    parser.add_argument("--name2", type=str, default="",
                        help="Name for the second point")

    # Road routing options
    parser.add_argument("--directions", action="store_true",
                        help="Show detailed turn-by-turn directions for road routes")

    args = parser.parse_args()

    # Check if road routing is requested but not available
    if args.mode in ["road", "both"] and not ROAD_ROUTING_AVAILABLE:
        print("Error: Road routing module not available. Install required dependencies.")
        return 1

    # Parse inputs
    try:
        if args.address:
            # Address mode
            if not args.start or not args.end:
                parser.error("Both start and end addresses are required with --address flag")

            start_address = args.start
            end_address = args.end if args.end else args.start_lon

            if not end_address:
                parser.error("End address is required")

            # Handle case where addresses might have been split
            if args.start_lon and not args.end:
                start_address = f"{args.start} {args.start_lon}"
                end_address = args.end if args.end else ""
            elif args.end_lon:
                end_address = f"{args.end} {args.end_lon}"

            start_coords = None
            end_coords = None
            start_name = start_address
            end_name = end_address

        else:
            # Coordinate mode
            if not all([args.start, args.start_lon, args.end, args.end_lon]):
                parser.error("Four coordinates required: lat1 lon1 lat2 lon2")

            try:
                lat1 = float(args.start)
                lon1 = float(args.start_lon)
                lat2 = float(args.end)
                lon2 = float(args.end_lon)
            except ValueError:
                parser.error("Coordinates must be numeric values")

            start_coords = (lat1, lon1)
            end_coords = (lat2, lon2)
            start_address = None
            end_address = None
            start_name = args.name1 if args.name1 else "Point A"
            end_name = args.name2 if args.name2 else "Point B"

    except Exception as e:
        print(f"Error parsing arguments: {e}")
        return 1

    # Execute routing based on mode
    try:
        # Road routing
        if args.mode in ["road", "both"]:
            print()  # Blank line for readability

            router = RoadRouter(transport_mode=args.transport)

            if args.address:
                route = router.route_by_address(start_address, end_address)
            else:
                route = router.route_by_coords(start_coords, end_coords)

            if route:
                # Use mi/km unit (road routing doesn't support nautical miles)
                road_unit = "mi" if args.unit == "mi" else "km"

                format_route_summary(route, unit=road_unit)

                if args.directions:
                    format_turn_by_turn(route, unit=road_unit)

                # Store for comparison
                if args.mode == "both":
                    road_distance_km = route.total_distance / 1000
                    road_duration = route.total_duration
            else:
                print("Failed to calculate road route.")
                if args.mode == "road":
                    return 1

        # Great circle routing
        if args.mode in ["great-circle", "both"]:
            # Get coordinates if we have addresses
            if args.address and not start_coords:
                print("\nGeocoding for great circle calculation...")
                geocoder = GeocodingService()

                start_result = geocoder.geocode(start_address)
                if start_result:
                    start_coords = (start_result[0], start_result[1])
                    if not args.name1:
                        start_name = start_result[2]

                end_result = geocoder.geocode(end_address)
                if end_result:
                    end_coords = (end_result[0], end_result[1])
                    if not args.name2:
                        end_name = end_result[2]

                if not start_coords or not end_coords:
                    print("Could not geocode addresses for great circle calculation")
                    return 1

            point1 = GeoPoint(start_coords[0], start_coords[1], start_name)
            point2 = GeoPoint(end_coords[0], end_coords[1], end_name)

            distance = ShortestPathCalculator.haversine_distance(point1, point2, args.unit)
            bearing = ShortestPathCalculator.initial_bearing(point1, point2)

            unit_names = {"km": "kilometers", "mi": "miles", "nm": "nautical miles"}
            unit_name = unit_names[args.unit]

            print("\n" + "=" * 70)
            print("GREAT CIRCLE DISTANCE (As The Crow Flies)")
            print("=" * 70)
            print(f"\nStarting Point: {point1}")
            print(f"Ending Point:   {point2}")
            print(f"\nDistance: {distance:.2f} {unit_name}")
            print(f"Initial Bearing: {format_bearing(bearing)}")

            if args.waypoints > 0:
                print(f"\n{'-' * 70}")
                print(f"WAYPOINTS (Great Circle Path)")
                print(f"{'-' * 70}")

                waypoints = ShortestPathCalculator.generate_waypoints(point1, point2, args.waypoints)

                for i, waypoint in enumerate(waypoints):
                    if i == 0:
                        print(f"\n  START: {waypoint}")
                    elif i == len(waypoints) - 1:
                        print(f"  END:   {waypoint}")
                    else:
                        segment_distance = ShortestPathCalculator.haversine_distance(point1, waypoint, args.unit)
                        print(f"  {i:2d}.    {waypoint}")
                        print(f"         Distance from start: {segment_distance:.2f} {unit_name}")

            print("\n" + "=" * 70 + "\n")

            # Comparison if both modes were calculated
            if args.mode == "both" and route:
                gc_distance_km = distance if args.unit == "km" else distance * 1.60934

                print("=" * 70)
                print("COMPARISON")
                print("=" * 70)
                print(f"\nGreat Circle (straight line): {gc_distance_km:.2f} km")
                print(f"Road Route ({args.transport}): {road_distance_km:.2f} km")
                print(f"Difference: {road_distance_km - gc_distance_km:.2f} km ({((road_distance_km/gc_distance_km - 1) * 100):.1f}% longer)")
                print(f"\nEstimated travel time: {route.format_duration()}")
                print("\n" + "=" * 70 + "\n")

    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
