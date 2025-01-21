//
// Created by Raphael Russo on 1/20/25.
//

#ifndef DASHBOARD_DEVICESECTION_H
#define DASHBOARD_DEVICESECTION_H
#pragma once
#include <QWidget>
#include <QLabel>
#include <QScrollArea>
#include <QHBoxLayout>
#include "DeviceButton.h"

class DeviceSection : public QWidget {
Q_OBJECT
public:
    explicit DeviceSection(const QString& category, QWidget* parent = nullptr)
            : QWidget(parent) {
        auto* layout = new QVBoxLayout(this);

        // Section header
        auto* header = new QLabel(category, this);
        header->setProperty("class", "section-header");
        layout->addWidget(header);

        // Scrollable device container
        auto* scrollArea = new QScrollArea(this);
        scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
        scrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        scrollArea->setWidgetResizable(true);

        auto* scrollContent = new QWidget(scrollArea);
        m_deviceLayout = new QHBoxLayout(scrollContent);
        m_deviceLayout->setSpacing(8);
        m_deviceLayout->setContentsMargins(4, 4, 4, 4);
        m_deviceLayout->addStretch();

        scrollArea->setWidget(scrollContent);
        layout->addWidget(scrollArea);
    }

    void addDevice(const DeviceInfo& device) {
        auto* button = new DeviceButton(device, this);
        m_deviceLayout->insertWidget(m_deviceLayout->count() - 1, button);
    }

    void clear() {
        while (QLayoutItem* item = m_deviceLayout->takeAt(0)) {
            delete item->widget();
            delete item;
        }
        m_deviceLayout->addStretch();
    }

private:
    QHBoxLayout* m_deviceLayout;
};


#endif //DASHBOARD_DEVICESECTION_H
