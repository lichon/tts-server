import time
import pyperclip
import pyttsx3
import os

def main():
    tts_service = LocalTTSService()
    last_content = ""
    while True:
        current_content = pyperclip.paste()
        if current_content != last_content:
            last_content = current_content
            tts_service.to_file(current_content)
        time.sleep(0.5)

def mpv_play(f):
    os.system("mpv --no-terminal --volume=150 --audio-device=wasapi/{a8b47dd6-3226-48db-9b72-862860a13f42} " + f)

class LocalTTSService:
    _file_idx = 1

    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        for v in self.voices:
            print("v", v)
        self.engine.setProperty('voice', 0)
        self.engine.setProperty('rate', 150)

    def set_voice(self):
        self.engine.setProperty('voice', 0)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_to_file(self, text):
        if not text:
            raise ValueError("Text cannot be empty")
        LocalTTSService._file_idx += 1
        filename = 'tmp_' + str(LocalTTSService._file_idx) + '.mp3'
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()
        mpv_play(filename)
        os.remove(filename)

if __name__ == "__main__":
    print("start monitoring clipboard")
    main()
