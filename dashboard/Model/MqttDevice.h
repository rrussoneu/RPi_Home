//
// Created by Raphael Russo on 10/27/24.
//

#ifndef DASHBOARD_MQTTDEVICE_H
#define DASHBOARD_MQTTDEVICE_H

#include <mqtt/async_client.h>


class MqttDevice {


private:
    std::string address;
    std::string client_id;
    std::string status_topic;
    std::string command_topic;

};


#endif //DASHBOARD_MQTTDEVICE_H
