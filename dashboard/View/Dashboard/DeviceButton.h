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
#include "Devices/DeviceInfo.h"

class DeviceButton : public QWidget {
Q_OBJECT
public:
    explicit DeviceButton(const DeviceInfo& device, QWidget* parent = nullptr)
            : QWidget(parent)
            , m_deviceId(device.id)
            , m_device(device) {
        auto* layout = new QVBoxLayout(this);
        layout->setSpacing(2);
        layout->setContentsMargins(4, 4, 4, 4);

        // Icon button
        m_iconButton = new QPushButton(this);
        updateIcon();  // Set initial icon based on state
        m_iconButton->setIconSize(QSize(32, 32));
        m_iconButton->setCheckable(true);
        m_iconButton->setChecked(device.isOn);
        m_iconButton->setFixedSize(48, 48);

        auto* buttonContainer = new QWidget(this);
        auto* buttonLayout = new QHBoxLayout(buttonContainer);
        buttonLayout->setContentsMargins(0, 0, 0, 0);
        buttonLayout->setSpacing(0);
        buttonLayout->addStretch();
        buttonLayout->addWidget(m_iconButton);
        buttonLayout->addStretch();

        layout->addWidget(buttonContainer);

        // Device name
        m_nameLabel = new QLabel(device.name, this);
        m_nameLabel->setAlignment(Qt::AlignCenter);
        m_nameLabel->setProperty("class", "device-label");
        m_nameLabel->setWordWrap(true);
        m_nameLabel->setMinimumWidth(80);
        m_nameLabel->setFixedHeight(24);
        layout->addWidget(m_nameLabel);

        // Room name
        m_roomLabel = new QLabel(device.room, this);
        m_roomLabel->setAlignment(Qt::AlignCenter);
        m_roomLabel->setProperty("class", "room-label");
        m_roomLabel->setWordWrap(true);
        m_roomLabel->setFixedHeight(20);
        layout->addWidget(m_roomLabel);

        // Set fixed width for the entire widget
        setFixedWidth(120);
        setMinimumHeight(110);

        connect(m_iconButton, &QPushButton::clicked,
                this, &DeviceButton::handleToggle);
    }

    // Update the device state and icon
    void updateState(bool isOn) {
        m_device.isOn = isOn;
        m_iconButton->setChecked(isOn);
        updateIcon();
    }

signals:
    void toggled(const QString& deviceId, bool isOn);

private slots:
    void handleToggle(bool checked) {
        m_device.isOn = checked;
        updateIcon();
        emit toggled(m_deviceId, checked);
    }

private:
    void updateIcon() {
        m_iconButton->setIcon(QIcon(m_device.getStateIcon()));
    }

    QString m_deviceId;
    DeviceInfo m_device;
    QPushButton* m_iconButton;
    QLabel* m_nameLabel;
    QLabel* m_roomLabel;
};

#endif //DASHBOARD_DEVICEBUTTON_H
