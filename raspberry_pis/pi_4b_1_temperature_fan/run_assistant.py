import os
import pvporcupine
import pyaudio
import struct
import subprocess
from openai import OpenAI  # https://platform.openai.com/docs/quickstart
import pygame
from luma.core.interface.serial import spi, noop
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
import numpy as np
from dotenv import load_dotenv
import time
import wave
import pygame
from pydub import AudioSegment
import threading
from common.topics import *
from common.RPi4 import RPi4


load_dotenv()

access_key = os.getenv('PORCUPINE_KEY')
client = OpenAI()

MOSQUITTO_BROKER=os.getenv('MOSQUITTO_BROKER')
MOSQUITTO_PORT=int(os.getenv('MOSQUITTO_PORT', '1883'))

# Initialize OLED display
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
device = sh1106(serial, width=128, height=64)

# Records some audio via pyaudio and is called after hearing the wake word
def record_audio(file_path, duration=5, sample_rate=16000):
    try:
        # Spinning motion while listening - on another thread so it can do both
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=display_spinner, args=(stop_spinner,))
        spinner_thread.start()

        # Record audio
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
        # Stop spinning
        stop_spinner.set()
        spinner_thread.join()

        # Clear the display after recording
        clear_display()

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
        print("No audio frames recorded.")

def display_spinner(stop_event):
    # Create frames for the spinner
    frames = []
    num_frames = 8
    radius = min(device.width, device.height) // 4
    center = (device.width // 2, device.height // 2)

    for i in range(num_frames):
        image = Image.new("1", (device.width, device.height))
        draw = ImageDraw.Draw(image)
        angle = (i / num_frames) * 360
        end_x = center[0] + radius * np.cos(np.radians(angle))
        end_y = center[1] + radius * np.sin(np.radians(angle))
        draw.line([center, (end_x, end_y)], fill=255, width=2)
        frames.append(image)

    frame_index = 0
    while not stop_event.is_set():
        device.display(frames[frame_index])
        frame_index = (frame_index + 1) % num_frames
        time.sleep(0.1)  # Sleep changes the speed

def clear_display():
    device.clear()
    

def display_idle_line():
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)
    midline = device.height // 2
    draw.line((0, midline, device.width - 1, midline), fill=255)
    device.display(image)

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
        display_idle_line()  # Display flat line when listening
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
        clear_display()  # Clear display after wake word is detected

    # Add a short delay for device release
    time.sleep(0.1)

def transcribe_audio(file_path):
    with open(file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

def get_llm_response(prompt_text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant with a wizardly flair."},
            {"role": "user", "content": prompt_text}
        ]
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def text_to_speech(text, file_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=text
    )
    response.stream_to_file(file_path)

def display_waveform(audio_chunk):
    # Flatten chunk
    data = audio_chunk.flatten().astype(np.float32)

    # Normalize to -1 to 1
    max_val = np.max(np.abs(data)) or 1  # Avoid division by zero
    normalized_data = data / max_val

    # Smooth data
    window_size = 5  # Size determines more or less smoothing
    cumsum_vec = np.cumsum(np.insert(normalized_data, 0, 0))
    smoothed_data = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size

    # Need to match width of the display
    num_points = len(smoothed_data)
    if num_points > device.width:
        factor = num_points // device.width
        sampled_data = smoothed_data[::factor][:device.width]
    else:
        sampled_data = np.interp(
            np.linspace(0, num_points - 1, device.width),
            np.arange(num_points),
            smoothed_data
        )

    # Scale data to fit display height
    scaled_data = ((sampled_data + 1) * (device.height - 1) / 2).astype(int)

    # Prepare the image
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)

    # Create points for the waveform
    x_values = np.arange(device.width)
    y_values = device.height - 1 - scaled_data  # Flip vertically to orient correctly
    points = list(zip(x_values, y_values))

    # Draw the waveform and display on screen
    if len(points) > 1:
        draw.line(points, fill=255)

    device.display(image)

def play_audio_with_waveform(file_path):

    pygame.mixer.init()

    # Load and play the audio file
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Get the audio data
    audio = AudioSegment.from_file(file_path)
    data = np.array(audio.get_array_of_samples())

    # Stereo vs mono reshaping
    if audio.channels > 1:
        data = data.reshape((-1, audio.channels))
        data = data.mean(axis=1)  # Convert to mono by averaging channels

    frame_rate = audio.frame_rate

    # Function for updating waveform
    def update_waveform():
        chunk_duration_ms = 30  # Update every 30 ms
        chunk_size = int(frame_rate * (chunk_duration_ms / 1000.0))
        total_length = len(data)
        current_pos = 0

        while current_pos < total_length and pygame.mixer.music.get_busy():
            chunk = data[current_pos:current_pos + chunk_size]
            if len(chunk) == 0:
                break
            display_waveform(chunk)
            current_pos += chunk_size
            pygame.time.wait(chunk_duration_ms)

        # Clear display post audio playback
        clear_display()

    # Start the waveform update in a separate thread
    waveform_thread = threading.Thread(target=update_waveform)
    waveform_thread.start()

    # Wait until the sound is done playing
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)

    # Make sure thread finishes
    waveform_thread.join()



# On connect for mosquitto
def on_local_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to Mosquitto MQTT broker")
    else:
        print(f"Failed to connect to Mosquitto MQTT broker, return code {rc}")

# On message for Mosquitto
def on_local_on_message(client, userdata, msg):
    return

commands = {
    "TURN ON THE LIGHT.": ("ON", HOME_DOOR_LIGHT_POWER),
    "TURN OFF THE LIGHT.": ("OFF", HOME_DOOR_LIGHT_POWER)
}

def check_command(prompt_text, client):
    res = commands.get(prompt_text.upper(), None)
    if res is not None:
        RPi4.publishMessage(client=client, topic=res[1], message=res[0])
        return True
    else:
        return False


def run_assistant(pi):
    '''
    pi = RPi4(device_id=1, name="living_room_pi")
    pi.addClient(
        "local_client", 
        broker=MOSQUITTO_BROKER, 
        port=MOSQUITTO_PORT, 
        on_connect=on_local_connect, 
        on_message=on_local_on_message, 
        tls=False, 
        client_id=""
        )
    '''

    handle = pvporcupine.create(access_key=access_key, keywords=['blueberry'])
    try:
        while True:
            # Listen for the wake word
            listen_for_wake_word(handle)

            # If the wake word was detected, record the next few seconds of audio/prompt
            prompt_fp = 'prompt.wav'
            record_audio(prompt_fp, duration=5)

            if not os.path.exists(prompt_fp):
                print("Recording failed: 'prompt.wav' not found.")
                continue  # Skip

            # Then turn it into text
            prompt_text = transcribe_audio(prompt_fp)

            print(prompt_text)

            # If this is a home automation command run the command with mosquitto
            if check_command(prompt_text, pi.getClient("local_client")):
                continue
            # Otherwise send to LLM
            else:
                # Get response from LLM
                response_text = get_llm_response(prompt_text)

                # Convert response to speech
                response_audio_file = 'response.mp3'
                text_to_speech(response_text, response_audio_file)

                # Play response
                play_audio_with_waveform(response_audio_file)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        handle.delete()
        clear_display()
