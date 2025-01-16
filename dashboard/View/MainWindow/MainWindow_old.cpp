#include "MainWindow_old.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QFrame>
#include <QFont>
#include <QDebug>
#include <QtCharts>
#include <QRandomGenerator>
#include <QGraphicsDropShadowEffect>

namespace Theme {
    const QString Primary = "#7B2CBF";
    const QString Secondary = "#9F7AEA";
    const QString Accent = "#4C1D95";
    const QString Background = "#F9F5FF";
    const QString CardBg = "#FFFFFF";
    const QString TextPrimary = "#4C1D95";
    const QString TextSecondary = "#6B7280";
    const QString Success = "#9F7AEA";

    const QString CardStyle = QString(
            "QFrame {"
            "    background-color: %1;"
            "    border-radius: 15px;"
            "    padding: 5px;"
            "}"
    ).arg(CardBg);

    const QString ButtonStyle = QString(
            "QPushButton {"
            "    background-color: %1;"
            "    color: white;"
            "    border-radius: 10px;"
            "    padding: 15px 5px;"
            "    font-weight: bold;"
            "    font-size: 9px;"
            "    min-width: 75px;"
            "    border: none;"
            "}"
            "QPushButton:hover {"
            "    background-color: %2;"
            "}"
            "QPushButton:checked {"
            "    background-color: %3;"
            "    border: none;"
            "}"
            "QPushButton:pressed {"
            "    background-color: %3;"
            "    border: none;"
            "}"
    ).arg(Secondary).arg(Primary).arg(Accent);
}

MainWindow_old::MainWindow_old(QWidget *parent)
        : QMainWindow(parent)
{
    setWindowTitle("Smart Home Dashboard");
    setMinimumSize(1024, 768);
    setStyleSheet(QString("QMainWindow { background-color: %1; }").arg(Theme::Background));
    setupUI();
}

void MainWindow_old::handleLightToggle(int lightIndex, bool isOn)
{
    qDebug() << "Light" << lightIndex + 1 << (isOn ? "turned on" : "turned off");
}
QChartView* MainWindow_old::createChart(const QString &title)
{
    auto chart = new QChart();
    auto series = new QSplineSeries();

    for (int i = 0; i < 10; ++i) {
        series->append(i, QRandomGenerator::global()->bounded(100));
    }

    series->setPen(QPen(QColor(Theme::Primary), 3));

    chart->addSeries(series);
    chart->setTitle(title);
    chart->setTitleFont(QFont("Inter", 12, QFont::Medium));
    chart->setTitleBrush(QBrush(QColor(Theme::TextPrimary)));

    chart->legend()->hide();
    chart->setBackgroundVisible(false);
    chart->setMargins(QMargins(3, 3, 3, 3));

    auto axisX = new QDateTimeAxis;
    axisX->setFormat("HH:mm");
    axisX->setTitleFont(QFont("Inter", 10));
    axisX->setLabelsFont(QFont("Inter", 9));
    axisX->setLabelsColor(QColor(Theme::TextSecondary));
    chart->addAxis(axisX, Qt::AlignBottom);
    series->attachAxis(axisX);

    auto axisY = new QValueAxis;
    axisY->setTitleFont(QFont("Inter", 10));
    axisY->setLabelsFont(QFont("Inter", 9));
    axisY->setLabelsColor(QColor(Theme::TextSecondary));
    chart->addAxis(axisY, Qt::AlignLeft);
    series->attachAxis(axisY);

    chart->setTheme(QChart::ChartThemeLight);

    auto chartView = new QChartView(chart);
    chartView->setRenderHint(QPainter::Antialiasing);
    chartView->setStyleSheet(Theme::CardStyle);

    auto shadow = new QGraphicsDropShadowEffect;
    shadow->setBlurRadius(15);
    shadow->setXOffset(0);
    shadow->setYOffset(2);
    shadow->setColor(QColor(0, 0, 0, 30));
    chartView->setGraphicsEffect(shadow);

    return chartView;
}

void MainWindow_old::setupUI()
{
    auto centralWidget = new QWidget(this);
    auto mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setSpacing(20);
    mainLayout->setContentsMargins(20, 20, 20, 20);

    // Title Section
    auto titleLabel = new QLabel("Smart Home Dashboard", this);
    titleLabel->setFont(QFont("Inter", 28, QFont::Bold));
    titleLabel->setStyleSheet(QString("color: %1;").arg(Theme::Accent));
    titleLabel->setAlignment(Qt::AlignLeft);
    titleLabel->setContentsMargins(0, 0, 0, 10);
    mainLayout->addWidget(titleLabel);

    // Controls Section
    auto controlsLayout = new QHBoxLayout();
    controlsLayout->setSpacing(20);

    // Lights Control Section
    auto lightsFrame = new QFrame(this);
    lightsFrame->setStyleSheet(Theme::CardStyle);
    lightsFrame->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Maximum);
    auto lightsLayout = new QVBoxLayout(lightsFrame);
    lightsLayout->setSpacing(10);
    lightsLayout->setContentsMargins(15, 15, 15, 15);

    auto lightsTitle = new QLabel("Lighting Control", this);
    lightsTitle->setFont(QFont("Inter", 16, QFont::DemiBold));
    lightsTitle->setStyleSheet(QString("color: %1;").arg(Theme::TextPrimary));
    lightsLayout->addWidget(lightsTitle);

    auto buttonContainer = new QHBoxLayout();
    buttonContainer->setSpacing(10);

    std::vector<QString> lights = {"Living Room", "Desk", "TV Area", "Bedroom", "Front Door"};
    for (int i = 0; i < 5; ++i) {
        auto lightBtn = new QPushButton(lights.at(i), this);
        lightBtn->setCheckable(true);
        lightBtn->setAutoExclusive(false);
        lightBtn->setStyleSheet(Theme::ButtonStyle);
        buttonContainer->addWidget(lightBtn);
        lightButtons.append(lightBtn);

        connect(lightBtn, &QPushButton::toggled, this, [this, i, lightBtn](bool checked) {
            handleLightToggle(i, checked);
            lightBtn->style()->unpolish(lightBtn);
            lightBtn->style()->polish(lightBtn);
        });
    }
    lightsLayout->addLayout(buttonContainer);
    controlsLayout->addWidget(lightsFrame);

    // Sensors Display Section
    auto sensorsFrame = new QFrame(this);
    sensorsFrame->setStyleSheet(Theme::CardStyle);
    sensorsFrame->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Maximum);
    auto sensorsLayout = new QHBoxLayout(sensorsFrame);
    sensorsLayout->setSpacing(30);
    sensorsLayout->setContentsMargins(15, 15, 15, 15);

    auto createSensorDisplay = [this](const QString &title, const QString &value) {
        auto layout = new QVBoxLayout();
        layout->setSpacing(2);

        auto titleLabel = new QLabel(title, this);
        titleLabel->setFont(QFont("Inter", 14, QFont::DemiBold));
        titleLabel->setStyleSheet(QString("color: %1;").arg(Theme::TextSecondary));

        auto valueLabel = new QLabel(value, this);
        valueLabel->setFont(QFont("Inter", 24, QFont::Bold));
        valueLabel->setStyleSheet(QString("color: %1;").arg(Theme::TextPrimary));

        layout->addWidget(titleLabel, 0, Qt::AlignLeft);
        layout->addWidget(valueLabel, 0, Qt::AlignLeft);
        return layout;
    };

    sensorsLayout->addLayout(createSensorDisplay("Temperature", "72°F"));
    sensorsLayout->addLayout(createSensorDisplay("Plant 1 Moisture", "55%"));
    sensorsLayout->addLayout(createSensorDisplay("Plant 2 Moisture", "62%"));
    controlsLayout->addWidget(sensorsFrame);

    mainLayout->addLayout(controlsLayout);

    // Graphs Section
    auto graphsLayout = new QGridLayout();
    graphsLayout->setSpacing(20);

    mainLayout->addLayout(graphsLayout);

    tempChart = createChart("Temperature");
    moistureChart1 = createChart("Plant 1 Moisture");
    moistureChart2 = createChart("Plant 2 Moisture");

    graphsLayout->addWidget(tempChart, 0, 0);
    graphsLayout->addWidget(moistureChart1, 0, 1);
    graphsLayout->addWidget(moistureChart2, 1, 0);

    tempChart->setMinimumHeight(200);
    moistureChart1->setMinimumHeight(200);
    moistureChart2->setMinimumHeight(200);

    setCentralWidget(centralWidget);
}