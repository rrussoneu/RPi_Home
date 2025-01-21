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
        layout->setContentsMargins(4, 4, 4, 4);

        // Icon button
        m_iconButton = new QPushButton(this);
        m_iconButton->setIcon(QIcon(device.iconPath));
        m_iconButton->setIconSize(QSize(32, 32));
        m_iconButton->setCheckable(true);
        m_iconButton->setChecked(device.isOn);
        m_iconButton->setFixedSize(48, 48);

        auto* buttonContainer = new QWidget(this);
        auto* buttonLayout = new QHBoxLayout(buttonContainer);
        buttonLayout->setContentsMargins(0, 0, 0, 0);
        buttonLayout->addStretch();
        buttonLayout->addWidget(m_iconButton);
        buttonLayout->addStretch();

        layout->addWidget(buttonContainer);

        // Device name
        m_nameLabel = new QLabel(device.name, this);
        m_nameLabel->setAlignment(Qt::AlignCenter);
        m_nameLabel->setWordWrap(true);
        m_nameLabel->setMinimumWidth(80);
        layout->addWidget(m_nameLabel);

        // Room name
        m_roomLabel = new QLabel(device.room, this);
        m_roomLabel->setAlignment(Qt::AlignCenter);
        m_roomLabel->setProperty("class", "room-label");
        m_roomLabel->setWordWrap(true);
        layout->addWidget(m_roomLabel);

        // Set fixed width for the entire widget
        setFixedWidth(120);
        setMinimumHeight(140);

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
    QLabel* m_nameLabel;
    QLabel* m_roomLabel;
};


#endif //DASHBOARD_DEVICEBUTTON_H
