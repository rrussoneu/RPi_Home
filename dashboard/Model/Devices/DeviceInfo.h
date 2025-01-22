//
// Created by Raphael Russo on 1/21/25.
//

#ifndef DASHBOARD_DEVICEINFO_H
#define DASHBOARD_DEVICEINFO_H
#pragma once
#include <QString>
#include <QMetaType>
#include <QVariantMap>
#include <QJsonObject>

struct DeviceInfo {
    QString id;          // Unique device identifier
    QString name;        // User friendly device name
    QString room;        // Device's room
    QString category;    // Device category (Lights, Fans, Sensors, etc.)
    QString type;        // Specific device type (OnOff, Dimmer, RGB, etc.)
    QString mqttTopic;   // MQTT topic for device communication
    QString iconPath;    // Path to device icon
    bool isOn;          // Current device state
    QVariantMap config;  // Any device specific config

    // Default constructor
    DeviceInfo() : isOn(false) {}

    // Constructor with essential fields
    DeviceInfo(const QString& deviceId,
               const QString& deviceName,
               const QString& deviceRoom,
               const QString& deviceCategory,
               const QString& iconfile,
               bool initialState = false,
               const QString& deviceType = "OnOff",
               const QString& topic = "",
               const QVariantMap& configuration = QVariantMap())
            : id(deviceId)
            , name(deviceName)
            , room(deviceRoom)
            , category(deviceCategory)
            , type(deviceType)
            , mqttTopic(topic)
            , iconPath(iconfile)
            , isOn(initialState)
            , config(configuration)
    {}

    // Helper method to create from JSON
    static DeviceInfo fromJson(const QJsonObject& json) {
        DeviceInfo info;
        info.id = json["id"].toString();
        info.name = json["name"].toString();
        info.room = json["room"].toString();
        info.category = json["category"].toString();
        info.type = json["type"].toString();
        info.mqttTopic = json["mqtt_topic"].toString();
        info.iconPath = json["icon_path"].toString();
        info.isOn = json["is_on"].toBool();

        if (json.contains("config")) {
            QJsonObject configObj = json["config"].toObject();
            for (auto it = configObj.begin(); it != configObj.end(); ++it) {
                info.config.insert(it.key(), it.value().toVariant());
            }
        }

        return info;
    }

    // Convert to JSON
    QJsonObject toJson() const {
        QJsonObject json;
        json["id"] = id;
        json["name"] = name;
        json["room"] = room;
        json["category"] = category;
        json["type"] = type;
        json["mqtt_topic"] = mqttTopic;
        json["icon_path"] = iconPath;
        json["is_on"] = isOn;

        if (!config.isEmpty()) {
            QJsonObject configObj;
            for (auto it = config.begin(); it != config.end(); ++it) {
                configObj.insert(it.key(), QJsonValue::fromVariant(it.value()));
            }
            json["config"] = configObj;
        }

        return json;
    }

    // Helper method to get icon based on state
    QString getStateIcon() const {
        // Base path without extension
        QString basePath = iconPath;
        basePath.replace("_on.svg", "").replace("_off.svg", "");

        // Return state icon
        return isOn ? basePath + "_on.svg" : basePath + "_off.svg";
    }
};

// For signals and slots
Q_DECLARE_METATYPE(DeviceInfo)
#endif //DASHBOARD_DEVICEINFO_H
