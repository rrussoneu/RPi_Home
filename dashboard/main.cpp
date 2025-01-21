#include <mqtt/async_client.h>
#include <iostream>
#include <chrono>
#include <thread>
#include <QApplication>
#include "View/MainWindow/MainWindow.h"

// The paho repo has lots of examples to go back and look at more


const std::string address = "10.0.0.170:1883";
const std::string client_id = "";
const std::string status_topic ="stat/home/door/light/POWER";
const std::string command_topic = "cmnd/home/door/light/POWER";

std::mutex mtx;
std::condition_variable cv;
bool status_received = false;
std::string current_status;

// Callback class
class callback : public virtual mqtt::callback {
public:
    mqtt::async_client& paho_client;

    callback(mqtt::async_client& client) : paho_client(client) {}

    void connection_lost(const std::string& cause) override {
        std::cout << "\nConnection lost";
        if (!cause.empty())
            std::cout << ". Cause: " << cause << std::endl;
        else
            std::cout << "." << std::endl;
    }

    void message_arrived(mqtt::const_message_ptr msg) override {
        std::string topic = msg->get_topic();
        std::string payload = msg->to_string();

        if (topic == status_topic) {
            std::cout << "Status received: " << payload << std::endl;

            // Update the current status
            {
                std::lock_guard<std::mutex> lock(mtx);
                current_status = payload;
                status_received = true;
            }
            cv.notify_one();
        }
    }

};

int main(int argc, char **argv) {
    /*
    mqtt::async_client client(address, client_id);

    // Set up callback
    callback cb(client);
    client.set_callback(cb);

    // Connect options
    mqtt::connect_options connOpts;
    connOpts.set_clean_session(true);

    try {
        // Connect to the broker
        std::cout << "Connecting to the MQTT broker at " << address << "..." << std::endl;
        mqtt::token_ptr conntok = client.connect(connOpts);
        conntok->wait();
        std::cout << "Connected" << std::endl;

        // Subscribe to the status topic
        client.subscribe(status_topic, 1)->wait();
        std::cout << "Subscribed to topic: " << status_topic << std::endl;

        // Publish an empty message to the command topic to request status
        mqtt::message_ptr status_request = mqtt::make_message(command_topic, "");
        status_request->set_qos(1);
        client.publish(status_request)->wait();
        std::cout << "Status request sent to " << command_topic << std::endl;

        // Wait for the status to be received with a timeout
        {
            std::unique_lock<std::mutex> lock(mtx);
            if(!cv.wait_for(lock, std::chrono::seconds(5), []{ return status_received; })) {
                std::cerr << "Timeout: Did not receive status within 5 seconds." << std::endl;
                client.disconnect()->wait();
                return 1;
            }
        }

        // Determine the opposite command
        std::string opposite_cmd;
        if (current_status == "ON") {
            opposite_cmd = "OFF";
        } else if (current_status == "OFF") {
            opposite_cmd = "ON";
        } else {
            std::cerr << "Error. Status received: " << current_status << std::endl;
            client.disconnect()->wait();
            return 1;
        }

        std::cout << "Current status: " << current_status << ". Sending command: " << opposite_cmd << std::endl;

        // Publish the opposite command
        mqtt::message_ptr cmd_msg = mqtt::make_message( command_topic, opposite_cmd);
        cmd_msg->set_qos(1);
        client.publish(cmd_msg)->wait();


        // Wait to make sure procesed
        std::this_thread::sleep_for(std::chrono::seconds(1));

        // Disconnect
        client.disconnect()->wait();
        std::cout << "Disconnected from the broker." << std::endl;
    }
    catch (const mqtt::exception& exc) {
        std::cerr << "MQTT Error: " << exc.what() << std::endl;
        return 1;
    }
    */
    // Also run the Qt Dashboard to check it
    QApplication app(argc, argv);

    MainWindow mainWindow;
    mainWindow.show();

    return app.exec();
}