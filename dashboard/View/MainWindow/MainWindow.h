//
// Created by Raphael Russo on 1/15/25.
//

#ifndef DASHBOARD_MAINWINDOW_H
#define DASHBOARD_MAINWINDOW_H


#include <QMainWindow>
#include <QStackedWidget>
#include "../../Controller/MainController.h"
#include "../Dashboard/DashboardView.h"

class MainWindow : public QMainWindow {

public:
    explicit MainWindow(MainController* controller, QWidget* parent = nullptr);
    ~MainWindow() override = default;


private slots:
    void navigateToView(int viewIndex);
    void handleDeviceStateChanged(const QString& deviceId);
    void handleConnectionStatus(bool connected);
    void showSettings();

private:
    void setupUi();
    void createActions();
    void createMenus();
    void createToolBar();
    void createStatusBar();
    void createDockWidgets();
    void setupTheme();

    // Core components
    MainController* m_controller;
    QStackedWidget* m_centralStack;
    QToolBar* m_mainToolbar;

    // Views
    std::unique_ptr<DashboardView> m_dashboardView;

    // Actions
    QAction* m_dashboardAction;
    QAction* m_devicesAction;
    QAction* m_gardenAction;
};


#endif //DASHBOARD_MAINWINDOW_H
