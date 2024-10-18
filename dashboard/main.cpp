#include <mqtt/async_client.h>
#include <iostream>

int main() {
    std::string address("10.0.0.170");
    std::string client_id("");

    mqtt::async_client client(address, client_id, MQTTVERSION_5);

    mqtt::connect_options connOpts;
    connOpts.set_clean_session(true);

    try {
        std::cout << "Connecting to server..." << std::endl;
        client.connect(connOpts)->wait();
        std::cout << "Connected" << std::endl;

        mqtt::message_ptr msg = mqtt::make_message("cmnd/home/door/light/POWER", "OFF");
        msg->set_qos(1);
        client.publish(msg)->wait();
        std::cout << "Msg published" << std::endl;

        client.disconnect()->wait();
        std::cout << "Disconnected" << std::endl;
    }
    catch (const mqtt::exception& exc) {
        std::cerr << "Error: " << exc.what() << std::endl;
        return 1;
    }

    return 0;
}