//
// Created by Raphael Russo on 1/15/25.
//

#ifndef DASHBOARD_DASHBOARDVIEW_H
#define DASHBOARD_DASHBOARDVIEW_H

#pragma once
#include "../BaseView.h"
#include <QVBoxLayout>
#include <QGridLayout>
#include <QLabel>

class DashboardView : public BaseView {
Q_OBJECT

public:
    explicit DashboardView(MainController* controller, QWidget* parent = nullptr)
            : BaseView(controller, parent)
    {
        setupUi();
    }


private:
    void setupUi()
    {
        auto* mainLayout = new QVBoxLayout(this);

        // Header
        auto* headerLabel = new QLabel("Dashboard", this);
        headerLabel->setProperty("class", "view-header");
        mainLayout->addWidget(headerLabel);

        // Grid for device and sensor widgets
        auto* grid = new QGridLayout();
        mainLayout->addLayout(grid);

        // Add some spacing and stretch
        mainLayout->addStretch();
    }


};


#endif //DASHBOARD_DASHBOARDVIEW_H
