//
// Created by Raphael Russo on 1/15/25.
//

#ifndef DASHBOARD_DASHBOARDVIEW_H
#define DASHBOARD_DASHBOARDVIEW_H

/**
 * Class for a view of the main dashboard
 */
#pragma once
#include <QWidget>
#include <QVBoxLayout>
#include <QScrollArea>
#include <QComboBox>
#include "DeviceSection.h"

class DashboardView : public QWidget {
Q_OBJECT
public:
    explicit DashboardView(QWidget* parent = nullptr);
    void updateDevices();
    void filterByRoom(const QString& room);

private slots:
    void showAddDeviceDialog();

private:
    void setupUi();
    void createRoomFilter();
    void createDeviceSections();

    QVBoxLayout* m_mainLayout;
    QComboBox* m_roomFilter;
    std::map<QString, DeviceSection*> m_deviceSections; // Category -> Section
    QPushButton* m_addDeviceButton;
};


#endif //DASHBOARD_DASHBOARDVIEW_H
