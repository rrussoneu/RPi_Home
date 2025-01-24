//
// Created by Raphael Russo on 1/23/25.
//

#include "AddDeviceDialog.h"
#include <QVBoxLayout>
#include <QFormLayout>
#include <QDialogButtonBox>
#include <QUuid>

AddDeviceDialog::AddDeviceDialog(QWidget* parent) : QDialog(parent) {
    setWindowTitle(tr("Add New Device"));
    setupUi();
}

void AddDeviceDialog::setupUi() {
    auto* layout = new QVBoxLayout(this);
    auto* formLayout = new QFormLayout;

    m_nameEdit = new QLineEdit(this);
    formLayout->addRow(tr("Device Name:"), m_nameEdit);

    m_roomCombo = new QComboBox(this);
    m_roomCombo->setEditable(true);
    m_roomCombo->addItems({"Living Room", "Bedroom", "Kitchen", "Office"});
    formLayout->addRow(tr("Room:"), m_roomCombo);

    m_categoryCombo = new QComboBox(this);
    m_categoryCombo->addItems({"Lights", "Fans", "Sensors", "Other"});
    formLayout->addRow(tr("Category:"), m_categoryCombo);

    m_topicEdit = new QLineEdit(this);
    m_topicEdit->setPlaceholderText("e.g., home/bedroom/light1");
    formLayout->addRow(tr("MQTT Topic:"), m_topicEdit);

    layout->addLayout(formLayout);

    auto* buttonBox = new QDialogButtonBox(
            QDialogButtonBox::Ok | QDialogButtonBox::Cancel,
            Qt::Horizontal, this);
    m_okButton = buttonBox->button(QDialogButtonBox::Ok);
    m_okButton->setEnabled(false);

    connect(buttonBox, &QDialogButtonBox::accepted, this, &QDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, this, &QDialog::reject);
    connect(m_nameEdit, &QLineEdit::textChanged, this, &AddDeviceDialog::validateInput);

    layout->addWidget(buttonBox);
}

void AddDeviceDialog::validateInput() {
    m_okButton->setEnabled(!m_nameEdit->text().trimmed().isEmpty());
}

DeviceInfo AddDeviceDialog::getDeviceInfo() const {
    QString id = QUuid::createUuid().toString(QUuid::WithoutBraces);
    QString category = m_categoryCombo->currentText();
    QString iconPath = QString(":/res/icons/%1").arg(
            category.toLower() == "lights" ? "light" :
            category.toLower() == "fans" ? "fan" :
            category.toLower() == "sensors" ? "sensor" : "device");

    return DeviceInfo(
            id,
            m_nameEdit->text().trimmed(),
            m_roomCombo->currentText().trimmed(),
            category,
            iconPath,
            false,
            "OnOff",
            m_topicEdit->text().trimmed()
    );
}