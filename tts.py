import subprocess
import time
import pyaudio
import pyperclip
import pyttsx3
import os
import tempfile
import logging

from pydub.utils import make_chunks

def init_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    os.environ['HTTPS_PROXY'] = 'http://192.168.1.1:8087'
    tts_service = LocalTTSService(use_ai=True)
    last_content = ''
    while True:
        current_content = pyperclip.paste()
        if current_content != last_content:
            last_content = current_content
            tts_service.speak(current_content)
        time.sleep(0.5)

def get_mpv_audio_device():
    ret = 'auto'
    device_list = subprocess.run([
        'mpv',
        '--audio-device=help',
    ], capture_output=True).stdout
    for device in device_list.splitlines():
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

def get_pyaudio_device():
    p = pyaudio.PyAudio()
    ret = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['hostApi'] == 0 and dev['name'].find('Steam Streaming Speakers') != -1:
            ret = dev['index']
            print(dev)
            break
    return ret

def pyaudio_play(seg, device = None):
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(seg.sample_width),
                    channels=seg.channels,
                    rate=seg.frame_rate,
                    output_device_index=device,
                    output=True)

    # Just in case there were any exceptions/interrupts, we release the resource
    # So as not to raise OSError: Device Unavailable should play() be used again
    try:
        for chunk in make_chunks(seg, 500):
            stream.write(chunk._data)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def _load_ai_engine(engine):
    try:
        import ai_tts_engine
        engine.proxy._module = ai_tts_engine
        engine.proxy._driver = ai_tts_engine.TTSDriver(engine.proxy)
        engine.setProperty('device', get_pyaudio_device())
    except ImportError:
        print("ai_tts_engine not found, using pyttsx3 instead")

class LocalTTSService:
    def __init__(self, use_ai=False, device='auto'):
        self.audio_device = 'auto'
        self.engine = pyttsx3.init()
        if use_ai:
            _load_ai_engine(self.engine)
        else:
            self.audio_device = device
        # setup microsoft voice
        voices = self.engine.getProperty('voices')
        if isinstance(voices, list):
            for i, v in enumerate(voices):
                if v.name.find('Microsoft Huihui Desktop') != -1:
                    print('set voice index', i)
                    self.engine.setProperty('voice', i)
                    self.engine.setProperty('rate', 200)
                    break

    def speak(self, text):
        if not text:
            return
        if self.audio_device == 'auto':
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            self.speak_to_file(text)

    def speak_to_file(self, text):
        if not text or len(text) == 0:
            return

        # Create temp file with .wav extension
        tmp_file = tempfile.NamedTemporaryFile(suffix='.wav')
        tmp_file.close()
        saved_file = tmp_file.name

        self.engine.save_to_file(text, saved_file)
        self.engine.runAndWait()
        mpv_play(saved_file, self.audio_device)
        if os.path.exists(saved_file):
            os.remove(saved_file)

if __name__ == '__main__':
    print('start monitoring clipboard')
    main()
