# VICINITY-AAU-VAS-Cleaning-Notification
This documentation describes the adapter of AAU VAS - Cleaning Notification.

# Infrastructure overview

Room usage data is collected through VICINITY by using one Tinymesh door sensor. A cleaning notification VAS will report it if the usage of the room over the threshold. 

Adapter serves as the interface between VICINITY and LabVIEW enabling to use all required interaction patterns.

![Image text](https://github.com/YajuanGuan/pics/blob/master/CleaningNotification.png)
      
# Configuration and deployment

Adapter runs on Python 3.6.

# Adapter changelog by version
Adapter releases are as aau_adapter_x.y.z.py

## 1.0.0
Start version, it works with agent-service-full-0.6.3.jar, and it subscribes to the events of Tinymesh door sensor status and publish a cleaning notification if the usage of the room reaches a threshold. 

# Functionality and API

## Publish an event to the subscribers. 
### Endpoint:
            PUT : /remote/objects/{oid}/events/{eid}
Publish the cleaning request and current time. 
### Return:
After subscribing the VAS successfully, the subscriber receives a response for instance:  
{  
    "clean": "required",  
    "time": "2018-11-10 11:30:29"  
}

