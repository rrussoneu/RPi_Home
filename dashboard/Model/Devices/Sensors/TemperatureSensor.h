//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_TEMPERATURESENSOR_H
#define DASHBOARD_TEMPERATURESENSOR_H

#include "Sensor.h"

class TemperatureSensor: public Sensor{
public:
    TemperatureSensor(const QString& id, const QString& name, const QString& room) : Sensor(id, name, room) {
        device_type = DeviceType::Temperature;
    }

};


#endif //DASHBOARD_TEMPERATURESENSOR_H
