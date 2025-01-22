//
// Created by Raphael Russo on 1/15/25.
//

#ifndef DASHBOARD_MAINWINDOW_H
#define DASHBOARD_MAINWINDOW_H
#pragma once
#include <QMainWindow>
#include <QDockWidget>
#include <QStackedWidget>
#include <QToolButton>
#include <QVBoxLayout>
#include <memory>
#include "../Dashboard/DashboardView.h"


class NavigationBar : public QWidget {
Q_OBJECT
public:
    explicit NavigationBar(QWidget* parent = nullptr) : QWidget(parent) {
        auto* layout = new QVBoxLayout(this);
        layout->setSpacing(8);
        layout->setContentsMargins(4, 8, 4, 8);

        createNavButton(":/res/icons/dashboard.svg", "Dashboard", 0);
        createNavButton(":/res/icons/devices.svg", "Devices", 1);
        createNavButton(":/res/icons/garden.svg", "Garden", 2);
        createNavButton(":/res/icons/camera.svg", "Camera", 3);
        createNavButton(":/res/icons/settings.svg", "Settings", 4);

        layout->addStretch();
        setFixedWidth(60);
        setProperty("class", "navigation-bar");
    }

signals:
    void navigationRequested(int index);

private:
    void createNavButton(const QString& iconPath, const QString& tooltip, int index) {
        auto* button = new QToolButton(this);
        button->setIcon(QIcon(iconPath));
        button->setIconSize(QSize(28, 28));
        button->setToolTip(tooltip);
        button->setCheckable(true);
        button->setToolButtonStyle(Qt::ToolButtonTextUnderIcon);
        button->setProperty("class", "navigation-button");
        button->setAutoExclusive(true);
        button->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
        button->setFixedHeight(60);
        if (index == 0) button->setChecked(true);

        connect(button, &QToolButton::clicked, this, [this, index]() {
            emit navigationRequested(index);
        });

        layout()->addWidget(button);
    }
};

class MainWindow : public QMainWindow {
Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private:
    void setupUi();
    void setupStyle();

    QDockWidget* m_navigationDock;
    QStackedWidget* m_centralStack;
    std::unique_ptr<DashboardView> m_dashboardView;
};

#endif //DASHBOARD_MAINWINDOW_H
