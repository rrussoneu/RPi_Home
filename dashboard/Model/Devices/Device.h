//
// Created by Raphael Russo on 10/17/24.
// A base class for general devices in an IoT smart home
//

#ifndef DASHBOARD_DEVICE_H
#define DASHBOARD_DEVICE_H
#pragma once
#include <QString>
#include <QObject>
#include <memory>
#include "DeviceInfo.h"

class DeviceState {
public:
    virtual ~DeviceState() = default;
    virtual QString toString() const = 0;
};

class OnOffState : public DeviceState {
public:
    explicit OnOffState(bool on = false) : m_isOn(on) {}
    bool isOn() const { return m_isOn; }
    void setOn(bool on) { m_isOn = on; }
    QString toString() const override {
        return m_isOn ? "ON" : "OFF";
    }
private:
    bool m_isOn;
};

class Device : public QObject {
Q_OBJECT
public:
    Device(const DeviceInfo& info)
            : m_id(info.id)
            , m_name(info.name)
            , m_room(info.room)
            , m_category(info.category)
            , m_online(false) {}

    virtual ~Device() = default;

    // Basic properties
    QString id() const { return m_id; }
    QString name() const { return m_name; }
    QString room() const { return m_room; }
    QString category() const { return m_category; }
    bool isOnline() const { return m_online; }

    // State management
    virtual bool updateState(const DeviceState& state) = 0;
    virtual std::shared_ptr<DeviceState> getState() const = 0;

    // Command handling
    virtual bool handleCommand(const QString& command, const QVariant& payload) = 0;

    void setOnline(bool online) {
        if (m_online != online) {
            m_online = online;
            emit onlineStatusChanged(m_online);
        }
    }

signals:
    void stateChanged(const DeviceState& state);
    void onlineStatusChanged(bool online);

protected:
    QString m_id;
    QString m_name;
    QString m_room;
    QString m_category;
    bool m_online;
};
#endif //DASHBOARD_DEVICE_H
