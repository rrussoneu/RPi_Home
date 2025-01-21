//
// Created by Raphael Russo on 1/15/25.
//
#include "MainWindow.h"
#include <QFile>
#include <QApplication>

MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    setupStyle();
    setupUi();
}

void MainWindow::setupUi() {
    // Set window properties
    setWindowTitle("Smart Home");
    resize(1280, 800);

    // Create navigation dock
    m_navigationDock = new QDockWidget(this);
    m_navigationDock->setFeatures(QDockWidget::NoDockWidgetFeatures);
    m_navigationDock->setAllowedAreas(Qt::LeftDockWidgetArea);
    m_navigationDock->setTitleBarWidget(new QWidget());
    auto* navigationBar = new NavigationBar(this);
    navigationBar->setProperty("class", "navigation-bar");
    m_navigationDock->setWidget(navigationBar);
    addDockWidget(Qt::LeftDockWidgetArea, m_navigationDock);

    // Create central stacked widget
    m_centralStack = new QStackedWidget(this);
    setCentralWidget(m_centralStack);

    // Create views
    m_dashboardView = std::make_unique<DashboardView>(this);

    // Add views to stack
    m_centralStack->addWidget(m_dashboardView.get());


    // Connect navigation signals
    connect(navigationBar, &NavigationBar::navigationRequested,
            m_centralStack, &QStackedWidget::setCurrentIndex);
}

void MainWindow::setupStyle() {
    QFile styleFile(":/res/styles/default.qss");
    if (!styleFile.open(QFile::ReadOnly | QFile::Text)) {
        qDebug() << "Failed to open stylesheet:" << styleFile.errorString();
        return;
    }
    QString style = styleFile.readAll();
    styleFile.close();

    // Apply the stylesheet
    qApp->setStyleSheet(style);

    // To debug any parsing issues
    if (style.isEmpty()) {
        qDebug() << "Stylesheet is empty";
    }
}