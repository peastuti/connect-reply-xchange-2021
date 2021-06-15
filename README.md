# How to empower old microcontrollers attaching them to the Cloud
### Connect Reply - Xchange 2021 - Show me how - Retrofitting

Hi there, this is the official repository of the Xchange Show Me How session that has been broadcasted on June 16th through the Reply's TV Systems held by @peastuti and @pquartarone.

This repo is intended to be as an easy guide and walkthrough the major techniques that are evolving the way of doing IoT. None of this code snippet could go in production, everything has the pure scope to demonstrate and prototype an architecture with Azure IoTHuB, DTDL, Azure Storage, Azure Event Hubs, Python, Grafana and InfluxDB.

If anything is missing, open an Issue or make a Pull Request, we'll try to keep this repo as updated as possible.

In particular, this project is composed of:
- `cloud-configuration` folder in which you will find a complete list of Azure resource that are needed and suggested to make this experiment work
- `dtdl_listener` folder that contains the Python script, that uses the Azure SDK for Python libraries, used to listen and intercept the DeviceTwin Update Events that flow through IoTHuB and Azure EventHubs
- `esp-azure` that is a submodule - a link - to the Espressif libraries that wrap the Azure SDK for C. It is the library that enable all the primitive communications with the Azure Cloud
- `flask-apis` another Python script using Flask used to emulate the backend APIs of our immaginary touchpoint. Two simple APIs to interact with the Azure DeviceTwin libraries to retrieve the current status of the device and to send a command to it.
- `influxdb-docker` contains all the settings and docker-compose file to setup a local instance of Grafana and InfluxDB. Used to store data received from the board time-wisely (InfluxDB) and to read the data in real-time.
- `iothub_devicetwin_example` is a complete C snippet inspired from an example of `esp-azure`. A working example of a board that connects to the wifi, sends events to the cloud via DeviceTwin every 20 seconds, and using a `status` parameters, sent from the Cloud, blink a led.

