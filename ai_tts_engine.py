#coding:utf-8
import os
import io
import time
import threading
import queue

import pyaudio
import numpy as np
import ChatTTS

from typing import Generator, Any

from pydub import AudioSegment
from pydub.utils import make_chunks

def main():
    import pyperclip
    os.environ['HTTPS_PROXY'] = 'http://192.168.1.1:8087'
    tts_engine = TTSDriver(None)
    last_content = ''
    while True:
        current_content = pyperclip.paste()
        if current_content != last_content:
            last_content = current_content
            tts_engine.say(current_content)
            #tts_engine.runAndWait()
            #play('output.wav')
        time.sleep(0.5)

def _play_with_pyaudio(seg, device):
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

def _get_wav_bytes(wav):
    b = io.BytesIO()
    if isinstance(wav, np.ndarray):
        np.save(b, wav)
        b.seek(0)
    elif isinstance(wav, str):
        with open(wav, 'rb') as f:
            b.write(f.read())
        # ignore wav header
        b.seek(36)
    else:
        raise ValueError("Unsupported type for wav: %s" % type(wav))
    return b

class ThreadedPlayer:
    def __init__(self, device, buffer_count=10):
        self.buffer_count = buffer_count
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.player = pyaudio.PyAudio()
        self.stream = self.player.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=22050,
                        output_device_index=device,
                        output=True)

    def _run(self):
        try:
            while True:
                item = self.queue.get()
                if isinstance(item, np.ndarray):
                    self._write_wav(item)
                else:
                    break
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.player.terminate()

    def play(self, generator: Generator[Any, None, None]):
        item_count = 0
        for item in generator:
            self.queue.put(item)
            item_count += 1
            if item_count == self.buffer_count:
                self.thread.start()

        self.queue.put(None)
        if not self.thread.is_alive():
            self.thread.start()

    def wait(self):
        self.thread.join()

    def _write_wav(self, wav):
        b = io.BytesIO()
        np.save(b, wav)
        b.seek(0)
        self.stream.write(b.getvalue())

    def __iter__(self):
        return self

class TTSDriver(object):
    def __init__(self, proxy):
        self._tts = ChatTTS.Chat()
        self._tts.load(compile=True, custom_path='ChatTTS')
        
        self.voice = self._tts.sample_random_speaker()
        self._proxy = proxy
        self._looping = False
        self._speaking = False
        self._stopping = False
        self.audio_device = None

    def destroy(self):
        self._tts=None

    def say(self, text):
        text = text + '[uv_break][lbreak]'
        params_infer_code = ChatTTS.Chat.InferCodeParams(
            spk_emb = self.voice, # add sampled speaker 
            temperature = .1,   # using custom temperature
            top_P = 0.9,        # top P decode
            top_K = 1,          # top K decode
        )
        params_refine_text = ChatTTS.Chat.RefineTextParams(
            prompt='[oral_0][laugh_2][break_7]',
        )

        wavs = self._tts.infer(text,
            stream=True,
            skip_refine_text=True,
            split_text=False,
            params_infer_code=params_infer_code,
            params_refine_text=params_refine_text
        )
        threaded_player = ThreadedPlayer(self.audio_device, buffer_count=10)
        threaded_player.play(wavs)
        threaded_player.wait()

    def stop(self):
        self.endLoop()

    def save_to_file(self, text, filename):
        # wavs = self._tts.infer(text)
        # assert len(wavs) == 1, "AI TTS only supports single wav output."
        raise NotImplementedError("save_to_file not implemented for AI TTS.")

    def getProperty(self, name):
        if name == 'voices':
            return None
        elif name == 'voice':
            return ''
        elif name == 'rate':
            return self._rateWpm
        elif name == 'volume':
            return self._tts.Volume / 100.0
        elif name == 'pitch':
            return self.pitch
            #print("Pitch adjustment not supported when using SAPI5")
        else:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
        if name == 'device':
            self.audio_device = value
        elif name == 'voice':
            pass
        elif name == 'rate':
            pass
        elif name == 'volume':
            pass
        elif name == 'pitch':
            pass
        else:
            raise KeyError('unknown property %s' % name)

    def startLoop(self):
        self._looping = True
        first = True
        while self._looping:
            if first:
                self._proxy.setBusy(False)
                first = False
            time.sleep(0.05)

    def endLoop(self):
        self._looping = False

    def iterate(self):
        self._proxy.setBusy(False)
        while 1:
            yield

if __name__ == '__main__':
    main()
