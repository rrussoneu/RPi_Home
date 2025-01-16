//
// Created by Raphael Russo on 1/15/25.
// Base class for one view of the dashboard
//

#ifndef DASHBOARD_BASEVIEW_H
#define DASHBOARD_BASEVIEW_H

#include <QWidget>
#include <memory>
#include "../../Controller/MainController.h"

class BaseView : public QWidget {
    Q_OBJECT

public:
    explicit BaseView(MainController *controller, QWidget *parent = nullptr)
    : QWidget(parent)
    , controller(controller)
    {
        setupBaseUi();
    }

    virtual void updateDevice(const QString &deviceId) = 0;
    virtual void refresh() = 0;

protected:
    MainController *controller;

    virtual void setupBaseUi() {
        setAttribute(Qt::WA_StyledBackground, true);
        setProperty("class", "base-view");
    }

    virtual void showError(const QString &message) {
        emit errorOccurred(message);
    }

signals:
    void errorOccurred(const QString &message);

};
#endif //DASHBOARD_BASEVIEW_H
