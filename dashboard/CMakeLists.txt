# dashboard/CMakeLists.txt

cmake_minimum_required(VERSION 3.16)

project(dashboard VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable Qt's automatic processing of MOC, UIC, and RCC files
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# Find Qt6 packages
find_package(Qt6 REQUIRED COMPONENTS
        Core
        Gui
        Widgets
        Charts
        Sql
        Network
)
find_package(OpenSSL REQUIRED)

# Find Paho MQTT C++ library
find_package(PahoMqttCpp REQUIRED CONFIG)

# Include directories for headers
include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/model
        ${CMAKE_CURRENT_SOURCE_DIR}/controllers
        ${CMAKE_CURRENT_SOURCE_DIR}/View/MainWindow
)

# Define source files with correct paths
set(PROJECT_SOURCES
        main.cpp
        View/MainWindow/MainWindow.cpp
        # Add other source files here if any
)

# Define header files with correct paths
set(PROJECT_HEADERS
        View/MainWindow/MainWindow.h
        Model/Devices/Device.h
        Model/Devices/CommandDevices/Light.h
        Model/Rooms/Room.h
        Model/Devices/CommandDevices/CommandDevice.h
        Model/Devices/CommandDevices/Fan.h
        Model/Devices/Sensors/Sensor.h
        Model/Devices/Sensors/SensorData.h
        Model/Devices/Sensors/MoistureSensor.h
        Model/MqttDevice.cpp
        Model/MqttDevice.h
        # Add other header files here if any
)

# Add executable using qt_add_executable for better integration
qt_add_executable(dashboard
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
        ${PROJECT_HEADERS}
)

# Link Qt libraries and Paho MQTT library

# Make sure to include Charts in your target_link_libraries
target_link_libraries(dashboard PRIVATE
        Qt6::Core
        Qt6::Gui
        Qt6::Widgets
        Qt6::Charts
        Qt6::Sql
        Qt6::Network
        PahoMqttCpp::paho-mqttpp3
        OpenSSL::SSL
        OpenSSL::Crypto
)

# Optionally, set RPATH properties if necessary
# set_target_properties(dashboard PROPERTIES
#     INSTALL_RPATH "/usr/local/lib"
#     BUILD_WITH_INSTALL_RPATH TRUE
#     INSTALL_RPATH_USE_LINK_PATH TRUE
# )

# Finalize the executable (required when using MANUAL_FINALIZATION)
qt_finalize_executable(dashboard)

# (Optional) Installation settings
include(GNUInstallDirs)
install(TARGETS dashboard
        BUNDLE DESTINATION .
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
