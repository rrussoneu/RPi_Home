//
// Created by Raphael Russo on 10/17/24.
// Class representing a room in a house
//

#ifndef DASHBOARD_ROOM_H
#define DASHBOARD_ROOM_H
#include <QString>
#include <QList>
#include "../Devices/Device.h"

class Room {
public:
    Room(const QString& name);
    QString getName() const;
    void addDevice(Device* device);
    QList<Device*> getDevices() const;

private:
    QString room_name;
    QList<Device*> devices;
};
#endif //DASHBOARD_ROOM_H
