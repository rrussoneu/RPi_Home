//
// Created by Raphael Russo on 1/20/25.
//

#ifndef DASHBOARD_DEVICEBUTTON_H
#define DASHBOARD_DEVICEBUTTON_H

#pragma once
#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>

struct DeviceInfo {
    QString id;
    QString name;
    QString room;
    QString category;
    QString iconPath;
    bool isOn;
};

class DeviceButton : public QWidget {
Q_OBJECT
public:
    explicit DeviceButton(const DeviceInfo& device, QWidget* parent = nullptr)
            : QWidget(parent), m_deviceId(device.id) {
        auto* layout = new QVBoxLayout(this);
        layout->setSpacing(4);

        // Icon button
        m_iconButton = new QPushButton(this);
        m_iconButton->setIcon(QIcon(device.iconPath));
        m_iconButton->setIconSize(QSize(48, 48));
        m_iconButton->setCheckable(true);
        m_iconButton->setChecked(device.isOn);
        layout->addWidget(m_iconButton);

        // Device name
        auto* nameLabel = new QLabel(device.name, this);
        nameLabel->setAlignment(Qt::AlignCenter);
        layout->addWidget(nameLabel);

        // Room name
        auto* roomLabel = new QLabel(device.room, this);
        roomLabel->setAlignment(Qt::AlignCenter);
        roomLabel->setProperty("class", "room-label");
        layout->addWidget(roomLabel);

        connect(m_iconButton, &QPushButton::clicked,
                this, &DeviceButton::handleToggle);
    }

signals:
    void toggled(const QString& deviceId, bool isOn);

private slots:
    void handleToggle(bool checked) {
        emit toggled(m_deviceId, checked);
    }

private:
    QString m_deviceId;
    QPushButton* m_iconButton;
};


#endif //DASHBOARD_DEVICEBUTTON_H
