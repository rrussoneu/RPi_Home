//
// Created by Raphael Russo on 1/23/25.
//

#ifndef DASHBOARD_ADDDEVICEDIALOG_H
#define DASHBOARD_ADDDEVICEDIALOG_H
#pragma once
#include <QDialog>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include "../Model/Devices/DeviceInfo.h"

class AddDeviceDialog : public QDialog {
Q_OBJECT
public:
    explicit AddDeviceDialog(QWidget* parent = nullptr);
    DeviceInfo getDeviceInfo() const;

private:
    void setupUi();
    void validateInput();

    QLineEdit* m_nameEdit;
    QComboBox* m_roomCombo;
    QComboBox* m_categoryCombo;
    QLineEdit* m_topicEdit;
    QPushButton* m_okButton;
};
#endif //DASHBOARD_ADDDEVICEDIALOG_H
