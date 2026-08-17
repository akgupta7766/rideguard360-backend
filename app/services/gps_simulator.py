import asyncio
import math
from datetime import datetime, timezone

from app.services.gps_service import update_bus_location


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
UPDATE_INTERVAL = 2


# Virtual bus speed in km/h
BUS_SPEED = 25


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
    print(
        f"Update : every {UPDATE_INTERVAL} seconds"
    )
    print("====================================")
    print()

    index = 0

    while True:

        current_lat, current_lon = ROUTE[index]

        if index < len(ROUTE) - 1:
            next_lat, next_lon = ROUTE[index + 1]

            heading = calculate_heading(
                current_lat,
                current_lon,
                next_lat,
                next_lon,
            )

        else:
            heading = 0

        gps_data = {
            "bus_id": BUS_ID,
            "latitude": current_lat,
            "longitude": current_lon,
            "speed": BUS_SPEED,
            "heading": heading,
        }

        try:

            result = await update_bus_location(
                gps_data
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

        # Restart route when destination reached
        if index >= len(ROUTE):
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