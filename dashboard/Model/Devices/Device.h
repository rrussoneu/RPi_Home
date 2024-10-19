//
// Created by Raphael Russo on 10/17/24.
// A base class for general devices in an IoT smart home
//

#ifndef DASHBOARD_DEVICE_H
#define DASHBOARD_DEVICE_H

#include <QString>
#include <QObject>

class Device : public QObject {
Q_OBJECT
public:
    enum class DeviceType { Light, Temperature, Moisture, Fan };

    Device(const QString& id, const QString& name, DeviceType type, const QString& room);
    virtual ~Device() = default;

    QString getId() const;
    QString getName() const;
    DeviceType getType() {
        return device_type;
    }
    QString getRoom() const;

signals:
    void statusChanged(const QString& deviceId, bool status);

protected:
    QString device_id;
    QString device_name;
    DeviceType device_type;
    QString device_room;
};

#endif //DASHBOARD_DEVICE_H
