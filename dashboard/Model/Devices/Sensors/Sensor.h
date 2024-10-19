//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_SENSOR_H
#define DASHBOARD_SENSOR_H
#include "../Device.h"
class Sensor : public Device {
public:
    Sensor(const QString& id, const QString& name, const QString& room);
    virtual double getCurrReading() = 0; // Get the most recent sensor value
    //virtual QVector<double> getHistoricalReadings() = 0; // Get historical data

    signals:
            void dataUpdated(); // Emit a signal on data update
};
#endif //DASHBOARD_SENSOR_H
