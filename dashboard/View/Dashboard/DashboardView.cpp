//
// Created by Raphael Russo on 1/15/25.
//

#include "DashboardView.h"
#include <QSet>

DashboardView::DashboardView(QWidget* parent)
        : QWidget(parent)
{
    setupUi();
}

void DashboardView::setupUi()
{
    m_mainLayout = new QVBoxLayout(this);
    m_mainLayout->setSpacing(16);
    m_mainLayout->setContentsMargins(16, 16, 16, 16);

    // Create room filter
    createRoomFilter();

    // Create device sections
    createDeviceSections();

    // Add stretch at the bottom
    m_mainLayout->addStretch();
}

void DashboardView::createRoomFilter() {
    auto* filterContainer = new QWidget(this);
    auto* filterLayout = new QHBoxLayout(filterContainer);

    auto* label = new QLabel(tr("Filter by Room:"), this);
    label->setProperty("class", "section-header");

    m_roomFilter = new QComboBox(this);
    m_roomFilter->addItem(tr("All Rooms"));

    filterLayout->addWidget(label);
    filterLayout->addWidget(m_roomFilter);
    filterLayout->addStretch();

    connect(m_roomFilter, QOverload<const QString&>::of(&QComboBox::currentTextChanged),
            this, &DashboardView::filterByRoom);

    m_mainLayout->addWidget(filterContainer);
}

void DashboardView::createDeviceSections()
{
    // Create sections for each category
    QStringList categories = {
            "Lights", "Fans", "Sensors", "Other"
    };

    for (const auto& category : categories) {
        auto* section = new DeviceSection(category, this);
        QLabel* header = section->findChild<QLabel*>();
        if (header) {
            header->setProperty("class", "section-header");
        }
        m_deviceSections[category] = section;
        m_mainLayout->addWidget(section);
    }
}

void DashboardView::updateDevices()
{
    // Clear all sections
    for (auto& [category, section] : m_deviceSections) {
        section->clear();
    }

    // Update room filter options
    QSet<QString> rooms;

    // Example devices (replace with actual device data)
    std::vector<DeviceInfo> devices = {
            {"light1", "Door Lamp", "Living Room", "Lights", ":/res/icons/lamp.svg", true},
            {"fan1", "Ceiling Fan", "Bedroom", "Fans", ":/res/icons/fan.svg", false},
    };

    // Add devices to appropriate sections
    for (const auto& device : devices) {
        rooms.insert(device.room);
        auto it = m_deviceSections.find(device.category);
        if (it != m_deviceSections.end()) {
            it->second->addDevice(device);
            QList<QLabel*> roomLabels = it->second->findChildren<QLabel*>();
            for (auto* label : roomLabels) {
                if (label->text() == device.room) {
                    label->setProperty("class", "room-label");
                }
            }
        }
    }

    // Update room filter options
    m_roomFilter->clear();
    m_roomFilter->addItem(tr("All Rooms"));
    for (const auto& room : rooms) {
        m_roomFilter->addItem(room);
    }
}

void DashboardView::filterByRoom(const QString& room)
{
    // Clear all sections
    for (auto& [category, section] : m_deviceSections) {
        section->clear();
    }

    // Example devices (replace with actual device data)
    std::vector<DeviceInfo> devices = {
            {"light1", "Door Lamp", "Living Room", "Lights", ":/res/icons/lamp.svg", true},
            {"fan1", "Ceiling Fan", "Bedroom", "Fans", ":/res/icons/fan.svg", false},
    };

    // Filter and add devices
    for (const auto& device : devices) {
        if (room == tr("All Rooms") || device.room == room) {
            auto it = m_deviceSections.find(device.category);
            if (it != m_deviceSections.end()) {
                it->second->addDevice(device);
            }
        }
    }
}
