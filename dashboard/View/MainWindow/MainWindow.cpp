//
// Created by Raphael Russo on 1/15/25.
//

#include "MainWindow.h"
#include <QApplication>
#include <QScreen>
#include <QFile>
#include <QStatusBar>
#include <QMessageBox>

MainWindow::MainWindow(MainController* controller, QWidget* parent)
        : QMainWindow(parent)
        , m_controller(controller)
{
    setupUi();
    setupTheme();

}