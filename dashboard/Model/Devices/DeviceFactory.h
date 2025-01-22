//
// Created by Raphael Russo on 1/21/25.
//

#ifndef DASHBOARD_DEVICEFACTORY_H
#define DASHBOARD_DEVICEFACTORY_H
#pragma once
#include <memory>
#include "Device.h"
#include "DeviceTypes/LightDevice.h"

class DeviceFactory {
public:
    std::shared_ptr<Device> createDevice(const DeviceInfo& info) {
        // Create appropriate device type based on category
        if (info.category == "Lights") {
            return std::make_shared<LightDevice>(info);
        }
        /*
        else if (info.category == "Fans") {
            return std::make_shared<FanDevice>(info);
        }
        else if (info.category == "Sensors") {
            return std::make_shared<SensorDevice>(info);
        }
         */
        return nullptr;
    }
};
#endif //DASHBOARD_DEVICEFACTORY_H
