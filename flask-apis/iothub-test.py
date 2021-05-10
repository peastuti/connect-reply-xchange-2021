import sys
from time import sleep
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, QuerySpecification, QueryResult

IOTHUB_CONNECTION_STRING = "HostName=iothub-raspy.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=BaR8uyMs+JBS1i3Zk7d+nsB9zoyuiO7YnL/K1YHPMU0="
DEVICE_ID = "raspi"

def iothub_service_sample_run():
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)

        new_tags = {
                'location' : {
                    'region' : 'IT',
                    'city' : 'Turin'
                }
            }

        twin = iothub_registry_manager.get_twin(DEVICE_ID)
        print(type(twin))
        print(twin)
        twin_patch = Twin(tags=new_tags, properties= TwinProperties(desired={'power_level' : 1}))
        twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

        # Add a delay to account for any latency before executing the query
        sleep(1)

        query_spec = QuerySpecification(query="SELECT * FROM devices WHERE tags.location.city = 'Turin'")
        query_result = iothub_registry_manager.query_iot_hub(query_spec, None, 100)
        print("Devices in Turin plant: {}".format(', '.join([twin.device_id for twin in query_result.items])))

    except Exception as ex:
        print("Unexpected error {0}".format(ex))
        return
    except KeyboardInterrupt:
        print("IoT Hub Device Twin service sample stopped")

if __name__ == '__main__':
    print("Starting the Python IoT Hub Device Twin service sample...")
    print()

    iothub_service_sample_run()
