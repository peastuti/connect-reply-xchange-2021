# Flask APIs with AzureSDK for Python

This really easy Python script uses [Flask](https://flask.palletsprojects.com/en/2.0.x/). Flask is a micro web framework. It is an amazing tool used to fast prototype things, exposing webservers and APIs.

Our aim was the one to produce something easy to read that could function as an example of a possible stable and secure production system written in Spring Boot, C#, or something else. 

We exposed two APIs, one to receive and forward a command and the other one to retrieve the current status of the device.
In this snippets we imported also the Azure SDK for Python to interact with the DeviceTwin interfaces. The result is described as follows:
- the first method is a `POST` endpoint, under the path `/<deviceId>/command` and it is used to send a command to the device. Specifying the DeviceId, that you previously mapped in Azure IoTHuB when you registered your first device, you're going to interact with the device directly. Whatever you're going to send in the `JSON` body will be written in the correspondent DeviceTwin instance that will be consequently consumed by the board itself. After the DeviceTwin patch, e.g., the DeviceTwin content change, it returns `OK`, otherwise `Not found!` if the `deviceId` doesn't exist.
- the second method is a `GET` endpoint, under the path `/<deviceId>/status` and it is used to retrieve the current status of the device. It returns all the content of the DeviceTwin reported properties, otherwise it returns `Not found!` if the `deviceId` doesn't exist.
