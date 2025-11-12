#!/usr/bin/env python3
"""
Global Shortest Path Calculator

This program calculates the shortest path between two geographic points
on Earth's surface using the great circle distance (Haversine formula).
"""

import math
import argparse
from typing import Tuple, List


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
        description="Calculate the shortest path between two geographic points on Earth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Distance from New York to London
  %(prog)s 40.7128 -74.0060 51.5074 -0.1278

  # Distance in miles with waypoints
  %(prog)s 40.7128 -74.0060 51.5074 -0.1278 --unit mi --waypoints 3

  # Named points
  %(prog)s 40.7128 -74.0060 51.5074 -0.1278 --name1 "New York" --name2 "London"
        """
    )

    parser.add_argument("lat1", type=float, help="Latitude of first point (-90 to 90)")
    parser.add_argument("lon1", type=float, help="Longitude of first point (-180 to 180)")
    parser.add_argument("lat2", type=float, help="Latitude of second point (-90 to 90)")
    parser.add_argument("lon2", type=float, help="Longitude of second point (-180 to 180)")
    parser.add_argument("--unit", choices=["km", "mi", "nm"], default="km",
                        help="Unit of measurement (km=kilometers, mi=miles, nm=nautical miles)")
    parser.add_argument("--waypoints", type=int, default=0,
                        help="Number of intermediate waypoints to generate")
    parser.add_argument("--name1", type=str, default="Point A",
                        help="Name for the first point")
    parser.add_argument("--name2", type=str, default="Point B",
                        help="Name for the second point")

    args = parser.parse_args()

    try:
        # Create geographic points
        point1 = GeoPoint(args.lat1, args.lon1, args.name1)
        point2 = GeoPoint(args.lat2, args.lon2, args.name2)

        # Calculate distance and bearing
        distance = ShortestPathCalculator.haversine_distance(point1, point2, args.unit)
        bearing = ShortestPathCalculator.initial_bearing(point1, point2)

        # Unit names for display
        unit_names = {"km": "kilometers", "mi": "miles", "nm": "nautical miles"}
        unit_name = unit_names[args.unit]

        # Display results
        print("\n" + "=" * 70)
        print("SHORTEST PATH CALCULATION (Great Circle Route)")
        print("=" * 70)
        print(f"\nStarting Point: {point1}")
        print(f"Ending Point:   {point2}")
        print(f"\nDistance: {distance:.2f} {unit_name}")
        print(f"Initial Bearing: {format_bearing(bearing)}")

        # Generate and display waypoints if requested
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

    except ValueError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
