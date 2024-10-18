//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_SENSORDATA_H
#define DASHBOARD_SENSORDATA_H
#include <QDateTime>

struct SensorData {
    QDateTime timestamp;
    double value;
};
#endif //DASHBOARD_SENSORDATA_H
