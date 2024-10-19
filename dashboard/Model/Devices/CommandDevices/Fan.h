//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_FAN_H
#define DASHBOARD_FAN_H
#include "CommandDevice.h"

// Fans should attach to the temperature widgets and rooms
class Fan : public CommandDevice {
Q_OBJECT
public:
    explicit Fan(const QString& id, const QString& name, const QString& room) : CommandDevice(id, name, room) {
        device_type = Device::DeviceType::Fan;
    }
};
#endif //DASHBOARD_FAN_H
