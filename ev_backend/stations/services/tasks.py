from celery import shared_task
from stations.models import ChargingStation
from stations.serializers import ChargingStationSerializer
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def process_bulk_charging_stations(data):
    """
    This task processes the charging stations data asynchronously
    and bulk creates the charging stations in the database.
    """
    try:
        charging_stations = []
        for item in data:
            # Assuming item is a dictionary with correct structure
            charging_stations.append(ChargingStation(**item))

        # Bulk create charging stations in batches (to avoid too many records in one go)
        batch_size = 100
        for i in range(0, len(charging_stations), batch_size):
            ChargingStation.objects.bulk_create(charging_stations[i:i+batch_size])
        return {"message": "Bulk upload successful"}

    except Exception as e:
        return {"error": str(e)}


def parse_json_lines(file_obj):
    for line in file_obj:
        if line.strip():  # Skip empty lines
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding error: {e}")
                print("Raw input:", repr(line))
                exit(1)

                continue
