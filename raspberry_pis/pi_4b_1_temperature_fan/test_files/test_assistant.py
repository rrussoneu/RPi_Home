import pvporcupine
import os
from dotenv import load_dotenv
import json

load_dotenv()

access_key=os.getenv('PORCUPINE_KEY')
# print(pvporcupine.KEYWORDS)
"""
Options for wake word: 
    {
        'computer', 'jarvis', 'terminator', 'hey siri', 'bumblebee', 
        'pico clock', 'grasshopper', 'alexa', 'grapefruit', 'hey google', 
        'ok google', 'picovoice', 'blueberry', 'americano', 'hey barista', 
        'porcupine'
    }
"""
handle = pvporcupine.create(access_key=access_key, keywords=['blueberry'])
