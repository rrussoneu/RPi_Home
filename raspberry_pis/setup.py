from setuptools import setup, find_packages

setup(
    name='common',  
    version='0.1.0',           
    packages=find_packages(),
    install_requires=[
        'paho-mqtt>=2.1.0',
        'Adafruit-Blinka>=8.47.0',
        'adafruit-circuitpython-dht>=4.0.4',
    ],
)