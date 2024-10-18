//
// Created by Raphael Russo on 10/17/24.
// Class representing a light
//

#ifndef DASHBOARD_LIGHT_H
#define DASHBOARD_LIGHT_H
#include "CommandDevice.h"

// Lights attach to rooms and have the general lights tab
class Light : public CommandDevice {
Q_OBJECT
public:
    explicit Light(const QString& id, const QString& name, const QString& room) : CommandDevice(id, name, room) {
        device_type = DeviceType::Light;
    }
};
#endif //DASHBOARD_LIGHT_H
