//
// Created by Raphael Russo on 1/21/25.
//

#ifndef DASHBOARD_LIGHTDEVICE_H
#define DASHBOARD_LIGHTDEVICE_H
#pragma once
#include "../Device.h"

class LightDevice : public Device {
    Q_OBJECT
public:
    explicit LightDevice(const DeviceInfo& info) : Device(info) {
        m_state = std::make_shared<OnOffState>(false);
    }

    bool updateState(const DeviceState& state) override {
        if (auto onOffState = dynamic_cast<const OnOffState*>(&state)) {
            m_state = std::make_shared<OnOffState>(onOffState->isOn());
            emit stateChanged(*m_state);
            return true;
        }
        return false;
    }

    std::shared_ptr<DeviceState> getState() const override {
        return m_state;
    }

    bool handleCommand(const QString& command, const QVariant& payload) override {
        if (command == "toggle") {
            auto currentState = std::dynamic_pointer_cast<OnOffState>(m_state);
            if (currentState) {
                currentState->setOn(!currentState->isOn());
                emit stateChanged(*currentState);
                return true;
            }
        }
        return false;
    }

private:
    std::shared_ptr<OnOffState> m_state;
};
#endif //DASHBOARD_LIGHTDEVICE_H
