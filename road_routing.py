#!/usr/bin/env python3
"""
Road Routing Module

This module provides road-based routing functionality using free APIs:
- Nominatim for geocoding addresses to coordinates
- OSRM (Open Source Routing Machine) for road routing
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class RouteStep:
    """Represents a single step in turn-by-turn directions."""
    instruction: str
    distance: float  # in meters
    duration: float  # in seconds
    location: Tuple[float, float]  # (lat, lon)

    def format_distance(self, unit: str = "km") -> str:
        """Format distance in the specified unit."""
        if unit == "mi":
            miles = self.distance / 1609.34
            if miles < 0.1:
                return f"{miles * 5280:.0f} feet"
            return f"{miles:.2f} miles"
        elif unit == "km":
            km = self.distance / 1000
            if km < 0.1:
                return f"{self.distance:.0f} meters"
            return f"{km:.2f} km"
        return f"{self.distance:.0f} meters"

    def format_duration(self) -> str:
        """Format duration in human-readable format."""
        minutes = int(self.duration / 60)
        seconds = int(self.duration % 60)

        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


@dataclass
class Route:
    """Represents a complete route with multiple steps."""
    steps: List[RouteStep]
    total_distance: float  # in meters
    total_duration: float  # in seconds
    start_location: Tuple[float, float]
    end_location: Tuple[float, float]
    geometry: Optional[List[Tuple[float, float]]] = None  # List of (lat, lon) points

    def format_distance(self, unit: str = "km") -> str:
        """Format total distance."""
        if unit == "mi":
            return f"{self.total_distance / 1609.34:.2f} miles"
        elif unit == "km":
            return f"{self.total_distance / 1000:.2f} km"
        return f"{self.total_distance:.0f} meters"

    def format_duration(self) -> str:
        """Format total duration."""
        minutes = int(self.total_duration / 60)
        hours = minutes // 60
        mins = minutes % 60

        if hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{minutes}m"


class GeocodingService:
    """Geocoding service using Nominatim (OpenStreetMap)."""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self):
        self.last_request_time = 0
        # Nominatim requires a User-Agent and rate limiting (max 1 req/sec)
        self.user_agent = "ShortestPathCalculator/1.0"

    def _rate_limit(self):
        """Ensure we don't exceed Nominatim's rate limit (1 request per second)."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0:
            time.sleep(1.0 - time_since_last)
        self.last_request_time = time.time()

    def geocode(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        Convert an address to coordinates.

        Args:
            address: Address string to geocode

        Returns:
            Tuple of (latitude, longitude, display_name) or None if not found
        """
        self._rate_limit()

        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', self.user_agent)

            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())

                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    display_name = result.get('display_name', address)
                    return (lat, lon, display_name)

                return None

        except urllib.error.URLError as e:
            print(f"Geocoding error: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing geocoding response: {e}")
            return None


class OSRMRoutingService:
    """Road routing service using OSRM (Open Source Routing Machine)."""

    # Public OSRM server - for production, consider self-hosting
    BASE_URL = "https://router.project-osrm.org"

    def __init__(self, profile: str = "car"):
        """
        Initialize OSRM routing service.

        Args:
            profile: Routing profile - 'car', 'bike', or 'foot'
        """
        if profile not in ['car', 'bike', 'foot']:
            raise ValueError("Profile must be 'car', 'bike', or 'foot'")
        self.profile = profile

    def get_route(self, start: Tuple[float, float], end: Tuple[float, float],
                  steps: bool = True, geometry: bool = True) -> Optional[Route]:
        """
        Get route between two coordinates.

        Args:
            start: Starting coordinates (lat, lon)
            end: Ending coordinates (lat, lon)
            steps: Include turn-by-turn steps
            geometry: Include route geometry

        Returns:
            Route object or None if routing failed
        """
        # OSRM uses lon,lat format (not lat,lon!)
        start_lonlat = f"{start[1]},{start[0]}"
        end_lonlat = f"{end[1]},{end[0]}"

        params = {
            'steps': 'true' if steps else 'false',
            'geometries': 'geojson',
            'overview': 'full' if geometry else 'false'
        }

        url = f"{self.BASE_URL}/route/v1/{self.profile}/{start_lonlat};{end_lonlat}"
        url += f"?{urllib.parse.urlencode(params)}"

        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'ShortestPathCalculator/1.0')

            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode())

                if data.get('code') != 'Ok':
                    print(f"Routing error: {data.get('message', 'Unknown error')}")
                    return None

                if not data.get('routes'):
                    return None

                route_data = data['routes'][0]

                # Parse steps
                route_steps = []
                if steps and 'legs' in route_data:
                    for leg in route_data['legs']:
                        for step_data in leg.get('steps', []):
                            maneuver = step_data.get('maneuver', {})
                            location = maneuver.get('location', [0, 0])

                            # Get instruction
                            instruction = step_data.get('name', 'Continue')
                            modifier = maneuver.get('modifier', '')
                            maneuver_type = maneuver.get('type', 'turn')

                            # Format instruction
                            if maneuver_type == 'depart':
                                instruction = f"Head {modifier} on {instruction}"
                            elif maneuver_type == 'arrive':
                                instruction = f"Arrive at destination"
                            elif maneuver_type == 'turn':
                                instruction = f"Turn {modifier} onto {instruction}"
                            elif maneuver_type == 'merge':
                                instruction = f"Merge {modifier}"
                            elif maneuver_type == 'roundabout':
                                instruction = f"Take roundabout onto {instruction}"
                            elif instruction:
                                instruction = f"Continue on {instruction}"

                            step = RouteStep(
                                instruction=instruction,
                                distance=step_data.get('distance', 0),
                                duration=step_data.get('duration', 0),
                                location=(location[1], location[0])  # Convert to lat,lon
                            )
                            route_steps.append(step)

                # Parse geometry
                route_geometry = None
                if geometry and 'geometry' in route_data:
                    coords = route_data['geometry'].get('coordinates', [])
                    # Convert from [lon, lat] to (lat, lon)
                    route_geometry = [(lat, lon) for lon, lat in coords]

                return Route(
                    steps=route_steps,
                    total_distance=route_data.get('distance', 0),
                    total_duration=route_data.get('duration', 0),
                    start_location=start,
                    end_location=end,
                    geometry=route_geometry
                )

        except urllib.error.URLError as e:
            print(f"Routing request error: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing routing response: {e}")
            return None


class RoadRouter:
    """High-level interface for road-based routing."""

    def __init__(self, transport_mode: str = "driving"):
        """
        Initialize road router.

        Args:
            transport_mode: 'driving', 'cycling', or 'walking'
        """
        self.geocoder = GeocodingService()

        # Map transport mode to OSRM profile
        profile_map = {
            'driving': 'car',
            'cycling': 'bike',
            'walking': 'foot'
        }

        if transport_mode not in profile_map:
            raise ValueError(f"Transport mode must be one of {list(profile_map.keys())}")

        self.transport_mode = transport_mode
        self.router = OSRMRoutingService(profile=profile_map[transport_mode])

    def route_by_address(self, start_address: str, end_address: str) -> Optional[Route]:
        """
        Calculate route between two addresses.

        Args:
            start_address: Starting address
            end_address: Ending address

        Returns:
            Route object or None if routing failed
        """
        print(f"Geocoding starting address: {start_address}")
        start_result = self.geocoder.geocode(start_address)
        if not start_result:
            print(f"Could not geocode starting address: {start_address}")
            return None

        start_coords = (start_result[0], start_result[1])
        start_name = start_result[2]

        print(f"Found: {start_name}")
        print(f"Geocoding destination address: {end_address}")

        end_result = self.geocoder.geocode(end_address)
        if not end_result:
            print(f"Could not geocode destination address: {end_address}")
            return None

        end_coords = (end_result[0], end_result[1])
        end_name = end_result[2]

        print(f"Found: {end_name}")
        print(f"\nCalculating {self.transport_mode} route...\n")

        return self.router.get_route(start_coords, end_coords)

    def route_by_coords(self, start: Tuple[float, float],
                       end: Tuple[float, float]) -> Optional[Route]:
        """
        Calculate route between two coordinate pairs.

        Args:
            start: Starting coordinates (lat, lon)
            end: Ending coordinates (lat, lon)

        Returns:
            Route object or None if routing failed
        """
        return self.router.get_route(start, end)


def format_route_summary(route: Route, unit: str = "km"):
    """Format and print a route summary."""
    print("=" * 70)
    print("ROAD ROUTE SUMMARY")
    print("=" * 70)
    print(f"\nTotal Distance: {route.format_distance(unit)}")
    print(f"Estimated Time: {route.format_duration()}")
    print(f"\nNumber of Steps: {len(route.steps)}")
    print("\n" + "=" * 70 + "\n")


def format_turn_by_turn(route: Route, unit: str = "km"):
    """Format and print turn-by-turn directions."""
    print("TURN-BY-TURN DIRECTIONS")
    print("=" * 70)

    cumulative_distance = 0

    for i, step in enumerate(route.steps, 1):
        cumulative_distance += step.distance

        # Don't show duration for very short steps
        if step.duration > 5:
            time_str = f" ({step.format_duration()})"
        else:
            time_str = ""

        print(f"\n{i:2d}. {step.instruction}")
        print(f"    {step.format_distance(unit)}{time_str}")

        # Show cumulative distance every few steps
        if i % 5 == 0 or i == len(route.steps):
            if unit == "mi":
                total = cumulative_distance / 1609.34
            else:
                total = cumulative_distance / 1000

            unit_name = "miles" if unit == "mi" else "km"
            print(f"    [Total: {total:.2f} {unit_name}]")

    print("\n" + "=" * 70 + "\n")
