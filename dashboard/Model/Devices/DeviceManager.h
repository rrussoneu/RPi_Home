//
// Created by Raphael Russo on 1/21/25.
//

#ifndef DASHBOARD_DEVICEMANAGER_H
#define DASHBOARD_DEVICEMANAGER_H


#pragma once
#include <QObject>
#include <QHash>
#include <memory>
#include "Device.h"
#include "DeviceInfo.h"
#include "DeviceFactory.h"


class DeviceManager : public QObject {
Q_OBJECT
public:
    static DeviceManager& instance() {
        static DeviceManager instance;
        return instance;
    }

    // Device management
    bool addDevice(const DeviceInfo& info);
    bool removeDevice(const QString& deviceId);
    std::shared_ptr<Device> getDevice(const QString& deviceId);
    DeviceInfo getDeviceInfo(const QString& deviceId) const;
    QList<DeviceInfo> getDevicesByRoom(const QString& room) const;
    QList<DeviceInfo> getDevicesByCategory(const QString& category) const;
    QStringList getRooms() const;
    QStringList getCategories() const;

    // State management
    bool updateDeviceState(const QString& deviceId, const DeviceState& state);
    //void setDeviceOnlineStatus(const QString& deviceId, bool online);

signals:
    void deviceAdded(const QString& deviceId);
    void deviceRemoved(const QString& deviceId);
    void deviceStateChanged(const QString& deviceId, const DeviceState& state);
    //void deviceOnlineStatusChanged(const QString& deviceId, bool online);

private:
    DeviceManager() = default;
    ~DeviceManager() = default;
    DeviceManager(const DeviceManager&) = delete;
    DeviceManager& operator=(const DeviceManager&) = delete;

    QHash<QString, std::shared_ptr<Device>> m_devices;
    QHash<QString, DeviceInfo> m_deviceInfos;
    DeviceFactory m_deviceFactory;
};


#endif //DASHBOARD_DEVICEMANAGER_H
