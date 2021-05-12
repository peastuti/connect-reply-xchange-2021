#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "azure_macro_utils/macro_utils.h"
#include "azure_c_shared_utility/threadapi.h"
#include "azure_c_shared_utility/platform.h"
#include "iothub_device_client.h"
#include "iothub_client_options.h"
#include "iothub.h"
#include "iothub_message.h"
#include "parson.h"
#include "sdkconfig.h"

#include "iothubtransportmqtt.h"

static const char* connectionString = CONFIG_IOTHUB_CONNECTION_STRING;
#define DOWORK_LOOP_NUM     3
typedef struct IOT_DEVICE_TAG
{
    char* status;           // desired property
    int interval;       // desired property
    int temperature;    // reported property
} IoTDevice;

IOTHUB_DEVICE_CLIENT_LL_HANDLE iotHubClientHandle;
IOTHUB_CLIENT_TRANSPORT_PROVIDER protocol = MQTT_Protocol;

int compare_status = 0;
int blink_interval = 0;


//  Converts the IoTDevice object into a JSON blob with reported properties that is ready to be sent across the wire as a twin.
static char* serializeToJson(IoTDevice* ioTDevice)
{
    char* result;

    JSON_Value* root_value = json_value_init_object();
    JSON_Object* root_object = json_value_get_object(root_value);

    // Only reported properties:
    (void)json_object_dotset_number(root_object, "temperature", ioTDevice->temperature);
    
    result = json_serialize_to_string(root_value);
    json_value_free(root_value);

    return result;
}

//  Converts the desired properties of the Device Twin JSON blob received from IoT Hub into a IoTDevice object.
static IoTDevice* parseFromJson(const char* json, DEVICE_TWIN_UPDATE_STATE update_state)
{
    IoTDevice* ioTDevice = malloc(sizeof(IoTDevice));
    JSON_Value* root_value = NULL;
    JSON_Object* root_object = NULL;

    if (NULL == ioTDevice)
    {
        (void)printf("ERROR: Failed to allocate memory\r\n");
    }

    else
    {
        (void)memset(ioTDevice, 0, sizeof(IoTDevice));

        root_value = json_parse_string(json);
        root_object = json_value_get_object(root_value);

        // Only desired properties:
        JSON_Value* status;
        JSON_Value* interval;

        if (update_state == DEVICE_TWIN_UPDATE_COMPLETE)
        {
            status = json_object_dotget_value(root_object, "desired.status");
            interval = json_object_dotget_value(root_object, "desired.interval");
        }
        else
        {
            status = json_object_dotget_value(root_object, "status");
            interval = json_object_dotget_value(root_object, "interval");
        }

        if (status != NULL)
        {
            const char* data = json_value_get_string(status);

            if (data != NULL)
            {
                ioTDevice->status = malloc(strlen(data) + 1);
                if (NULL != ioTDevice->status)
                {
                    (void)strcpy(ioTDevice->status, data);
                }
            }
        }
        if (interval != NULL)
        {
            ioTDevice->interval = (int)json_value_get_number(interval);
        }

        json_value_free(root_value);
    }

    return ioTDevice;
}

static void deviceTwinCallback(DEVICE_TWIN_UPDATE_STATE update_state, const unsigned char* payLoad, size_t size, void* userContextCallback)
{
    (void)update_state;
    (void)size;
    IoTDevice* oldIoTDevice = (IoTDevice*)userContextCallback;
    IoTDevice* newIoTDevice = parseFromJson((const char*)payLoad, update_state);

    if (newIoTDevice != NULL)
    {
        if (newIoTDevice->status != NULL)
        {
            if ((oldIoTDevice->status != NULL) && (strcmp(oldIoTDevice->status, newIoTDevice->status) != 0))
            {
                free(oldIoTDevice->status);
                oldIoTDevice->status = NULL;
            }

            if (oldIoTDevice->status == NULL)
            {   
                printf("\n-----------\n");
                printf("\nReceived a new status = %s\n", newIoTDevice->status);
                printf("\n-----------\n\n");
                
                compare_status = strcmp(newIoTDevice->status, "LOW");

                if ( NULL != (oldIoTDevice->status = malloc(strlen(newIoTDevice->status) + 1)))
                {
                    (void)strcpy(oldIoTDevice->status, newIoTDevice->status);
                    free(newIoTDevice->status);
                }
            }
        }

        if (newIoTDevice->interval != 0)
        {
            if (newIoTDevice->interval != oldIoTDevice->interval)
            {
                printf("Received a new interval = %d\n", newIoTDevice->interval);
                oldIoTDevice->interval = newIoTDevice->interval;
                blink_interval = newIoTDevice->interval;
            }
        }


        free(newIoTDevice);
    }
    else
    {
        printf("Error: JSON parsing failed!\r\n");
    }
}

static void reportedstatusCallback(int status_code, void* userContextCallback)
{
    (void)userContextCallback;
    printf("\t- Response: %d\n", status_code);
    // printf("Device Twin reported properties update completed with result: %d\r\n", status_code);
}

static void iothub_client_device_twin(void)
{
    
    if (IoTHub_Init() != 0)
    {
        (void)printf("Failed to initialize the platform.\r\n");
    }
    else
    {
        if ((iotHubClientHandle = IoTHubDeviceClient_LL_CreateFromConnectionString(connectionString, protocol)) == NULL)
        {
            (void)printf("ERROR: iotHubClientHandle is NULL!\r\n");
        }
        else
        {
            IoTDevice ioTDevice;
            memset(&ioTDevice, 0, sizeof(IoTDevice));
            srand(time(NULL));
            ioTDevice.temperature = (u_int8_t)rand()%(100);

            char* reportedProperties = serializeToJson(&ioTDevice);
            if (reportedProperties != NULL)
            {
                (void)IoTHubDeviceClient_LL_SendReportedState(iotHubClientHandle, (const unsigned char*)reportedProperties, strlen(reportedProperties), reportedstatusCallback, NULL);
                (void)IoTHubDeviceClient_LL_SetDeviceTwinCallback(iotHubClientHandle, deviceTwinCallback, &ioTDevice);


                while (1) {
                    IoTHubDeviceClient_LL_DoWork(iotHubClientHandle);
                    ThreadAPI_Sleep(10);
                }

                free(reportedProperties);
            }
            else
            {
                printf("Error: JSON serialization failed!\r\n");
            }
            IoTHubDeviceClient_LL_Destroy(iotHubClientHandle);
        }

        IoTHub_Deinit();
    }
}

int send_reported_telemetry(void)
{

    IoTDevice ioTDevice;
    memset(&ioTDevice, 0, sizeof(IoTDevice));
    srand(time(NULL));
    ioTDevice.temperature = (u_int8_t)rand()%(100);

    printf("Sending new temperature telemetry: %d\t", ioTDevice.temperature);

    char* reportedProperties = serializeToJson(&ioTDevice);
    if (reportedProperties != NULL)
    {

        (void)IoTHubDeviceClient_LL_SendReportedState(iotHubClientHandle, (const unsigned char*)reportedProperties, strlen(reportedProperties), reportedstatusCallback, NULL);

        free(reportedProperties);
    }
    else
    {
        printf("Error: JSON serialization failed!\r\n");
    }

    return 0;
}

int get_blink_flag(void)
{
    return compare_status;
}

int get_blink_interval(void)
{
    return blink_interval;
}

int iothub_client_device_twin_init(void)
{
    iothub_client_device_twin();
    return 0;
}