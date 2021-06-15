# IoTHUB DeviceTwin Change Events Listener

This very trivial Python scripts reads all the events that flows through the IoTHub and EventHubs.

You can find more of them in the link that follows 
https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py

An app using [Asyncio](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/recv_with_checkpoint_store_async.py) is started. A callback for the event is declared.
Whenever a new event arrives, the callback extract the important information from the message, such as `deviceId` and `temperature` that is our telemetry in the example. Then it invokes an auxiliary method that is `save_on_influx(deviceId, temperature)` and it saves the points after creating the correct device structure.

At the top you will notice the Azure EventHubs and Azure Storage connections strings and names.
Also, before starting the execution, a connection to a local instance of InfluxDB is performed. It is suggested to start the docker-compose environment before executing this script.

