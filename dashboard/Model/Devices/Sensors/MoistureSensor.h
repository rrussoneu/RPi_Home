//
// Created by Raphael Russo on 10/17/24.
//

#ifndef DASHBOARD_MOISTURESENSOR_H
#define DASHBOARD_MOISTURESENSOR_H

#include "Sensor.h"

class MoistureSensor: public Sensor{
public:
    MoistureSensor(const QString& id, const QString& name, const QString& room) : Sensor(id, name, room) {
        device_type = DeviceType::Moisture;
    }

};
#endif //DASHBOARD_MOISTURESENSOR_H
