//
// Created by Raphael Russo on 1/21/25.
//

#include "DeviceManager.h"
#include <QDebug>

bool DeviceManager::addDevice(const DeviceInfo& info) {
    if (m_devices.contains(info.id)) {
        qDebug() << "Device with ID" << info.id << "already exists";
        return false;
    }

    auto device = m_deviceFactory.createDevice(info);
    if (!device) {
        qDebug() << "Failed to create device for category:" << info.category;
        return false;
    }

    m_devices[info.id] = device;

    // Store the device info for later reference
    m_deviceInfos[info.id] = info;

    emit deviceAdded(info.id);
    return true;
}

bool DeviceManager::removeDevice(const QString& deviceId) {
    if (!m_devices.contains(deviceId)) {
        return false;
    }

    m_devices.remove(deviceId);
    m_deviceInfos.remove(deviceId);
    emit deviceRemoved(deviceId);
    return true;
}

std::shared_ptr<Device> DeviceManager::getDevice(const QString& deviceId) {
    return m_devices.value(deviceId);
}

DeviceInfo DeviceManager::getDeviceInfo(const QString& deviceId) const {
    return m_deviceInfos.value(deviceId);
}

QList<DeviceInfo> DeviceManager::getDevicesByRoom(const QString& room) const {
    QList<DeviceInfo> devices;
    for (const auto& info : m_deviceInfos) {
        if (info.room == room) {
            devices.append(info);
        }
    }
    return devices;
}

QList<DeviceInfo> DeviceManager::getDevicesByCategory(const QString& category) const {
    QList<DeviceInfo> devices;
    for (const auto& info : m_deviceInfos) {
        if (info.category == category) {
            devices.append(info);
        }
    }
    return devices;
}

QStringList DeviceManager::getRooms() const {
    QSet<QString> rooms;
    for (const auto& info : m_deviceInfos) {
        rooms.insert(info.room);
    }
    return rooms.values();
}

QStringList DeviceManager::getCategories() const {
    QSet<QString> categories;
    for (const auto& info : m_deviceInfos) {
        categories.insert(info.category);
    }
    return categories.values();
}

bool DeviceManager::updateDeviceState(const QString& deviceId, const DeviceState& state) {
    auto device = getDevice(deviceId);
    if (!device) {
        return false;
    }

    if (device->updateState(state)) {
        emit deviceStateChanged(deviceId, state);
        return true;
    }
    return false;
}
