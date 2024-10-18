//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_COMMANDDEVICE_H
#define DASHBOARD_COMMANDDEVICE_H
#include "../Device.h"
class CommandDevice : public Device {
    Q_OBJECT
public:
    CommandDevice(const QString& id, const QString& name, const QString& room);

    bool isOn() const {
        return device_on;
    }
    void setState(bool on) {
        device_on = on;
        emit onStateChanged(device_on);
    }

signals:
    void onStateChanged(bool on);

protected:
    bool device_on;
};
#endif //DASHBOARD_COMMANDDEVICE_H
