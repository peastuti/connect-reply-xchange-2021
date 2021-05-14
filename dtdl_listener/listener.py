# https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py

import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from influxdb import InfluxDBClient

class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

CONNECTION_STR = "Endpoint=sb://xchange2021.servicebus.windows.net/;SharedAccessKeyName=iothubroutes_xchange2021;SharedAccessKey=8FBiKfet5mdQsv0qQ6ptSY6myc2pKW0rRg/2C+w20gU=;EntityPath=xchange2021hub"
EVENTHUB_NAME = "xchange2021hub"
STORAGE_CONNECTION_STR = "DefaultEndpointsProtocol=https;AccountName=xchange2021;AccountKey=7jZXlQR41UYfiZgeQbz417ZvfaiLHtApidbXnVE0U6UlHW+HClnk/KQgSRXsKN+DRx7jMtLhl1RGXERyq0QGgg==;EndpointSuffix=core.windows.net"
BLOB_CONTAINER_NAME = "xchange2021"

influx_client = InfluxDBClient('localhost', 8086, 'admin', 'password', 'xchange')
influx_client.switch_database('xchange')

def save_on_influx(deviceId, temperature):
    element = [{
        "measurement": "Telemetry",
        "tags": {
            "deviceId": deviceId
        },
        "fields": {
            "temperature": temperature
        }
    }]
    if influx_client.write_points(element, time_precision='ms'):
        print(f"Successfully saved!\n\n")

async def on_event(partition_context, event):
    try:
        await partition_context.update_checkpoint(event)

        deviceId = str(event.properties[b'deviceId'].decode('utf-8'))
        current_temperature = int(event.body_as_json(encoding='UTF-8')['properties']['reported']['temperature'])

        print(f"{bc.OKGREEN}----> Received new event from: {bc.BOLD}{deviceId}.{bc.ENDC}")
        print(f"{bc.OKBLUE}-> New Reported Temperarature: {bc.BOLD}{current_temperature}.{bc.ENDC}")

        print(f"{bc.UNDERLINE}Let's save it in DB now!{bc.ENDC}\n")
        save_on_influx(deviceId, current_temperature)
    except Exception:
        pass


async def receive(client):
    """
    Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
    a checkpoint store, the client will load-balance partition assignment with other EventHubConsumerClient instances
    which also try to receive events from all partitions and use the same storage resource.
    """
    await client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )
    # With specified partition_id, load-balance will be disabled, for example:
    # await client.receive(on_event=on_event, partition_id='0'))


async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing.
    )
    async with client:
        await receive(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())