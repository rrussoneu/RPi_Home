import os
import pvporcupine
import pyaudio
import struct
import subprocess
from openai import OpenAI # https://platform.openai.com/docs/quickstart
import pygame
from luma.core.interface.serial import spi, noop
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
import numpy as np
from dotenv import load_dotenv
import time
import wave
import pygame

load_dotenv()

access_key=os.getenv('PORCUPINE_KEY')
client = OpenAI()

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

# Records some audio via pyaudio and is called after hearing the wake word 
def record_audio(file_path, duration=5, sample_rate=16000):
    try:
        # Record the audio
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=sample_rate,
                         input=True,
                         frames_per_buffer=1024)

        print(f"Recording for {duration} seconds...")
        frames = []

        for _ in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)

        print("Recording complete.")
    except Exception as e:
        print(f"Error during recording: {e}")
    finally:
        # Close resources
        stream.stop_stream()
        stream.close()
        pa.terminate()

    # Save the recorded data
    if frames:
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Recording saved to {file_path}")
    else:
        print("No audio frames recorded :O")

# Plays back audio using pygame
def play_audio(file_path):
    # Load and play file
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Keep going until it's done playing back
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def listen_for_wake_word(porcupine):
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for wake word...")
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                break
    finally:
        # Properly close stream
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        print("Audio stream closed after wake word was detected")

    # Add a short delay for device release
    time.sleep(0.1)

def transcribe_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
            )
    return transcription.text

# Uses OpenAI api to get a response to a given prompt
def get_llm_response(prompt_text):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant with a wizardly flair."},
        {
            "role": "user",
            "content": prompt_text
        }
        ]
    )
    print( completion.choices[0].message.content)
    return completion.choices[0].message.content

# Turns text to speech with another OpenAI api call
def text_to_speech(text, file_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=text
    )

    response.stream_to_file(file_path)

def main():
    handle = pvporcupine.create(access_key=access_key, keywords=['blueberry'])
    try:
        while True:
            # Listen for the wake word
            listen_for_wake_word(handle)
            
            # If the wake word was detected record the next few seconds of audio/ prompt
            prompt_fp = 'prompt.wav'
            record_audio(prompt_fp, duration=5)

            if not os.path.exists(prompt_fp):
                print("Recording failed: 'prompt.wav' not found.")
                continue  # Skip

            # Then turn it into text
            prompt_text = transcribe_audio(prompt_fp)

            # Debugging print
            # print(f"Heard: {prompt_text}")


            # Get response from llm 
            response_text = get_llm_response(prompt_text)

            # Convert response to speech
            response_audio_file = 'response.mp3'
            text_to_speech(response_text, response_audio_file)

            # Play response
            play_audio(response_audio_file)
    
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        handle.delete()


if __name__ == "__main__":
    main()

