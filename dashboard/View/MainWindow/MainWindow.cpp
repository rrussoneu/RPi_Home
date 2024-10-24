#include "MainWindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QLabel>
#include <QFrame>
#include <QFont>
#include <QDebug>
#include <QtCharts>
#include <QRandomGenerator>


MainWindow::MainWindow(QWidget *parent)
        : QMainWindow(parent)
{
    setWindowTitle("Home Portal");
    setMinimumSize(800, 600);
    setupUI();
}

void MainWindow::handleLightToggle(int lightIndex, bool isOn)
{
    /*
     * ToDo:
     *  - Create light objects with MQTT topics and base the toggle on their on or off state
     *  - Enable toggling to switch the light state
     *
    */

    qDebug() << "Light" << lightIndex + 1 << (isOn ? "turned on" : "turned off");
}

QChartView* MainWindow::createChart(const QString &title)
{
    auto chart = new QChart();
    auto series = new QLineSeries();

    // Add sample data using QRandomGenerator
    for (int i = 0; i < 10; ++i) {
        series->append(i, QRandomGenerator::global()->bounded(100));
    }

    chart->addSeries(series);
    chart->setTitle(title);
    chart->legend()->hide();

    auto axisX = new QDateTimeAxis;
    axisX->setFormat("HH:mm");
    chart->addAxis(axisX, Qt::AlignBottom);
    series->attachAxis(axisX);

    auto axisY = new QValueAxis;
    chart->addAxis(axisY, Qt::AlignLeft);
    series->attachAxis(axisY);

    chart->setTheme(QChart::ChartThemeLight);

    auto chartView = new QChartView(chart);
    chartView->setRenderHint(QPainter::Antialiasing);
    return chartView;
}

void MainWindow::setupUI()
{
    auto centralWidget = new QWidget(this);
    auto mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setSpacing(20);
    mainLayout->setContentsMargins(20, 20, 20, 20);

    // Title
    auto titleLabel = new QLabel("Smart Home Dashboard", this);
    auto titleFont = QFont("Arial", 24, QFont::Bold);
    titleLabel->setFont(titleFont);
    titleLabel->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(titleLabel);

    // Lights Control
    auto lightsFrame = new QFrame(this);
    lightsFrame->setFrameStyle(QFrame::StyledPanel | QFrame::Raised);
    lightsFrame->setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 10px; }");
    auto lightsLayout = new QHBoxLayout(lightsFrame);

    QString buttonStyle =
            "QPushButton {"
            "   background-color: #e0e0e0;"
            "   border-radius: 15px;"
            "   padding: 10px;"
            "   min-width: 100px;"
            "}"
            "QPushButton:checked {"
            "   background-color: #4CAF50;"
            "   color: white;"
            "}";

    // Light buttons with slots
    std::vector<QString> lights = {"Living Room Lamp", "Desk Lamp", "TV Lamp", "Bedroom Lamp", "Front Lamp"};
    for (int i = 0; i < 5; ++i) {
        auto lightBtn = new QPushButton(lights.at(i), this);
        lightBtn->setCheckable(true);
        lightBtn->setStyleSheet(buttonStyle);
        lightsLayout->addWidget(lightBtn);
        lightButtons.append(lightBtn);

        connect(lightBtn, &QPushButton::toggled, this, [this, i](bool checked) {
            handleLightToggle(i, checked);
        });
    }
    mainLayout->addWidget(lightsFrame);

    // Sensors Display Section
    auto sensorsFrame = new QFrame(this);
    sensorsFrame->setFrameStyle(QFrame::StyledPanel | QFrame::Raised);
    sensorsFrame->setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 10px; }");
    auto sensorsLayout = new QHBoxLayout(sensorsFrame);

    // Temperature Display
    auto tempLayout = new QVBoxLayout();
    auto tempLabel = new QLabel("Temperature", this);
    tempLabel->setFont(QFont("Arial", 12, QFont::Bold));
    auto tempValue = new QLabel("72°F", this);
    tempValue->setFont(QFont("Arial", 24));
    tempLayout->addWidget(tempLabel, 0, Qt::AlignCenter);
    tempLayout->addWidget(tempValue, 0, Qt::AlignCenter);
    sensorsLayout->addLayout(tempLayout);

    // Moisture Displays
    for (int i = 0; i < 2; ++i) {
        auto moistureLayout = new QVBoxLayout();
        auto moistureLabel = new QLabel(QString("Plant %1 Moisture").arg(i), this);
        moistureLabel->setFont(QFont("Arial", 12, QFont::Bold));
        auto moistureValue = new QLabel("55%", this);
        moistureValue->setFont(QFont("Arial", 24));
        moistureLayout->addWidget(moistureLabel, 0, Qt::AlignCenter);
        moistureLayout->addWidget(moistureValue, 0, Qt::AlignCenter);
        sensorsLayout->addLayout(moistureLayout);
    }
    mainLayout->addWidget(sensorsFrame);

    // Graphs Section
    auto graphsLayout = new QGridLayout();
    graphsLayout->setSpacing(10);

    tempChart = createChart("Temperature History");
    moistureChart1 = createChart("Plant 1 Moisture History");
    moistureChart2 = createChart("Plant 2 Moisture History");

    graphsLayout->addWidget(tempChart, 0, 0);
    graphsLayout->addWidget(moistureChart1, 0, 1);
    graphsLayout->addWidget(moistureChart2, 1, 0);

    mainLayout->addLayout(graphsLayout);
    setCentralWidget(centralWidget);
}