//
// Created by Raphael Russo on 1/22/25.
//
#include "DeviceController.h"


void DeviceController::toggleDevice(const QString& deviceId, bool state) {
    auto& manager = DeviceManager::instance();
    auto device = manager.getDevice(deviceId);
    if (device) {
        auto onOffState = std::make_shared<OnOffState>(state);
        device->updateState(*onOffState);
        emit deviceStateChanged(deviceId, state);
    }
}

void DeviceController::updateDeviceState(const QString& deviceId, bool state) {
    auto& manager = DeviceManager::instance();
    auto deviceInfo = manager.getDeviceInfo(deviceId);
    deviceInfo.isOn = state;
    emit deviceStateChanged(deviceId, state);
}
