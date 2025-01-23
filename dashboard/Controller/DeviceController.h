//
// Created by Raphael Russo on 1/22/25.
//

#ifndef DASHBOARD_DEVICECONTROLLER_H
#define DASHBOARD_DEVICECONTROLLER_H
#pragma once
#include <QObject>
#include "../model/Devices/DeviceManager.h"

class DeviceController : public QObject {
Q_OBJECT
public:
    static DeviceController& instance() {
        static DeviceController instance;
        return instance;
    }

    void toggleDevice(const QString& deviceId, bool state);
    void updateDeviceState(const QString& deviceId, bool state);

signals:
    void deviceStateChanged(const QString& deviceId, bool state);

private:
    DeviceController() = default;
};
#endif //DASHBOARD_DEVICECONTROLLER_H
