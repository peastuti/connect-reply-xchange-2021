from flask import Flask, request

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties

IOTHUB_CONNECTION_STRING = "YourIoTHuBConnectionString"

app = Flask(__name__)

@app.route('/<deviceId>/command', methods = ['POST'])
def command(deviceId):
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)
        twin = iothub_registry_manager.get_twin(deviceId)

        twin_patch = Twin(properties= TwinProperties(desired=request.get_json()))
        twin = iothub_registry_manager.update_twin(deviceId, twin_patch, twin.etag)

        return "OK"
    except Exception:
        return "Not found!"

@app.route('/<deviceId>/status', methods = ['GET'])
def status(deviceId):
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)
        twin = iothub_registry_manager.get_twin(deviceId)

        return twin.properties.reported
    except Exception:
        return "Not found!"
    
if __name__ == "__main__":
    app.run(debug=True)
