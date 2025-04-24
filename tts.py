import subprocess
import time
import pyperclip
import pyttsx4
import os
import tempfile

def main():
    tts_service = LocalTTSService()
    last_content = ''
    while True:
        current_content = pyperclip.paste()
        if current_content != last_content:
            last_content = current_content
            tts_service.to_file(current_content)
        time.sleep(0.5)

def get_audio_device():
    ret = 'auto'
    device_list = subprocess.run([
        'mpv',
        '--audio-device=help',
    ], capture_output=True).stdout
    for device in device_list.splitlines():
        print(device)
        if b'Steam Streaming Speakers' in device:
            ret = device.decode('utf-8').strip().split(' ')[0].strip("'")
            print("selected device:", ret)
            break
    return ret

def mpv_play(f, device = 'auto'):
    subprocess.run([
        'mpv',
        '--audio-device=' + device,
        '--no-terminal',
        '--force-window=no',
        '--volume=150', f
    ])

class LocalTTSService:
    def __init__(self):
        self.audio_device = get_audio_device()
        self.engine = pyttsx4.init()
        voices = self.engine.getProperty('voices')
        if isinstance(voices, list):
            for v in voices:
                print('v', v)
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_to_file(self, text):
        if not text:
            raise ValueError('Text cannot be empty')

        # Create temp file with .wav extension
        tmp_file = tempfile.NamedTemporaryFile(suffix='.wav')
        tmp_file.close()
        saved_file = tmp_file.name

        self.engine.save_to_file(text, saved_file)
        self.engine.runAndWait()
        mpv_play(saved_file, self.audio_device)
        os.remove(saved_file)

if __name__ == '__main__':
    print('start monitoring clipboard')
    main()
