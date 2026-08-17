import asyncio
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


# This script is run directly, so app.main's dotenv setup does not execute.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ==========================================
# VIRTUAL BUS CONFIGURATION
# ==========================================

BUS_ID = "6a807ebe6caf72374fa39f05"

# Demo route coordinates
# Each tuple = (latitude, longitude)

ROUTE = [
    (28.6139, 77.2090),
    (28.6148, 77.2102),
    (28.6160, 77.2115),
    (28.6172, 77.2130),
    (28.6185, 77.2145),
    (28.6200, 77.2160),
    (28.6215, 77.2178),
    (28.6230, 77.2195),
    (28.6245, 77.2210),
    (28.6260, 77.2225),
]


# Time between GPS updates
UPDATE_INTERVAL = 1


# Virtual bus speed in km/h
BUS_SPEED = 25


GPS_API_BASE_URL = os.getenv(
    "GPS_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")
GPS_SIMULATOR_TOKEN = os.getenv("GPS_SIMULATOR_TOKEN")
GPS_SIMULATOR_API_KEY = os.getenv("GPS_SIMULATOR_API_KEY")


def post_gps_update(gps_data: dict) -> dict:
    if not GPS_SIMULATOR_API_KEY and not GPS_SIMULATOR_TOKEN:
        raise RuntimeError(
            "Set GPS_SIMULATOR_API_KEY or GPS_SIMULATOR_TOKEN"
        )

    headers = {"Content-Type": "application/json"}

    if GPS_SIMULATOR_API_KEY:
        headers["X-GPS-Simulator-Key"] = GPS_SIMULATOR_API_KEY
    else:
        headers["Authorization"] = f"Bearer {GPS_SIMULATOR_TOKEN}"

    request = Request(
        f"{GPS_API_BASE_URL}/api/gps/update",
        data=json.dumps(gps_data).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GPS update failed with HTTP {error.code}: {detail}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Unable to reach GPS API: {error.reason}"
        ) from error


# ==========================================
# CALCULATE HEADING
# ==========================================

def calculate_heading(
    lat1,
    lon1,
    lat2,
    lon2,
):
    delta_lon = math.radians(lon2 - lon1)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    x = math.sin(delta_lon) * math.cos(lat2_rad)

    y = (
        math.cos(lat1_rad)
        * math.sin(lat2_rad)
        - math.sin(lat1_rad)
        * math.cos(lat2_rad)
        * math.cos(delta_lon)
    )

    heading = math.degrees(
        math.atan2(x, y)
    )

    return (heading + 360) % 360


def distance_in_metres(lat1, lon1, lat2, lon2):
    earth_radius = 6_371_000
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius * math.asin(math.sqrt(a))


def build_simulation_points():
    points = []
    metres_per_update = (BUS_SPEED * 1000 / 3600) * UPDATE_INTERVAL

    for index, (start_lat, start_lon) in enumerate(ROUTE):
        end_lat, end_lon = ROUTE[(index + 1) % len(ROUTE)]
        steps = max(
            1,
            round(
                distance_in_metres(
                    start_lat, start_lon, end_lat, end_lon
                ) / metres_per_update
            ),
        )
        heading = calculate_heading(start_lat, start_lon, end_lat, end_lon)

        for step in range(steps):
            progress = step / steps
            points.append((
                start_lat + (end_lat - start_lat) * progress,
                start_lon + (end_lon - start_lon) * progress,
                heading,
            ))

    return points


# ==========================================
# SIMULATOR
# ==========================================

async def run_simulator():

    print()
    print("====================================")
    print("      RIDEGUARD 360 GPS SIMULATOR")
    print("====================================")
    print(f"Bus ID : {BUS_ID}")
    print(f"Speed  : {BUS_SPEED} km/h")
    print(f"API    : {GPS_API_BASE_URL}")
    print(
        "Auth   : "
        f"{'API key' if GPS_SIMULATOR_API_KEY else 'JWT token' if GPS_SIMULATOR_TOKEN else 'MISSING'}"
    )
    print(
        f"Update : every {UPDATE_INTERVAL} seconds"
    )
    print("====================================")
    print()

    route_points = build_simulation_points()
    index = 0

    while True:

        current_lat, current_lon, heading = route_points[index]

        gps_data = {
            "bus_id": BUS_ID,
            "latitude": current_lat,
            "longitude": current_lon,
            "speed": BUS_SPEED,
            "heading": heading,
        }

        try:

            result = await asyncio.to_thread(
                post_gps_update,
                gps_data,
            )

            if result:

                timestamp = datetime.now(
                    timezone.utc
                ).strftime(
                    "%H:%M:%S"
                )

                print(
                    f"[{timestamp}] "
                    f"BUS-001 | "
                    f"Lat: {current_lat:.6f} | "
                    f"Lon: {current_lon:.6f} | "
                    f"Speed: {BUS_SPEED} km/h"
                )

            else:

                print(
                    "❌ Bus not found"
                )

        except Exception as error:

            print(
                f"❌ GPS update failed: {error}"
            )

        index += 1

        # Restart the continuous route when destination is reached.
        if index >= len(route_points):
            print()
            print(
                "🔄 Route completed. "
                "Restarting virtual bus..."
            )
            print()

            index = 0

        await asyncio.sleep(
            UPDATE_INTERVAL
        )


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    asyncio.run(
        run_simulator()
    )
