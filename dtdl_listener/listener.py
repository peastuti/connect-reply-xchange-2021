import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
import json
from pprint import pprint
from influxdb import InfluxDBClient

influx_client = InfluxDBClient('localhost', 8086, 'admin', 'admin', 'nestle')
influx_client.switch_database('nestle')

def save_on_influx(deviceId, temperature):
    element = {
        "measurement": "Contacts",
        "tags": {
            "deviceId": deviceId
        },
        "fields": {
            "temperature": temperature
        }
    }
    influx_client.write_points(element, time_precision='ms')

async def on_event(partition_context, event):
    
    print(f"\n\n----> Received new event from {event.properties[b'deviceId'].decode('utf-8')}")
    current_temperature = event.body_as_json(encoding='UTF-8')['properties']['reported']['temperature']
    print( f"New Reported Temperarature {current_temperature}.")

    # print("Let's save it in DB now!")
    # save_on_influx(event.properties[b'deviceId'].decode('utf-8'), current_temperature)

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)

async def main():
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string("DefaultEndpointsProtocol=https;AccountName=raspydeviceeventsstorage;AccountKey=w/wY+D0mKKNlq8nijzcSnjnFddAGF/pRPwN940XRztG8tRXNlp8tjPLdyaKq9HmD5DhvZP++5I+a7xO6rzHATQ==;EndpointSuffix=core.windows.net", "event-hub-checkpoint")

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string("Endpoint=sb://raspy-device-event.servicebus.windows.net/;SharedAccessKeyName=iothubroutes_iothub-raspy;SharedAccessKey=4O/QSuPX9czzKFTHu7mTibERb3NaL0tbZW8dwDkek28=;EntityPath=raspy_device_events", consumer_group="$Default", eventhub_name="raspy_device_events", checkpoint_store=checkpoint_store)
    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(on_event=on_event,  starting_position="-1")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(main())    