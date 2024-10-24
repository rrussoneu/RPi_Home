#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QVector>
#include <QPushButton>
#include <QtCharts>

class MainWindow : public QMainWindow {
Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() = default;

private slots:
    void handleLightToggle(int lightIndex, bool isOn);

private:
    void setupUI();
    QChartView* createChart(const QString &title);

    QVector<QPushButton*> lightButtons;
    QChartView *tempChart;
    QChartView *moistureChart1;
    QChartView *moistureChart2;
};

#endif // MAINWINDOW_H