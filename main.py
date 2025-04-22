import pathlib
import tts
import keyboard

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
tts_service = tts.LocalTTSService()


def on_ctrl_0():
    tts_service.speak_to_file("紧急情况退出")

def on_ctrl_1():
    tts_service.speak_to_file("")

def on_ctrl_2():
    tts_service.speak_to_file("")

def on_ctrl_3():
    tts_service.speak_to_file("")

def on_ctrl_4():
    tts_service.speak_to_file("")

def on_ctrl_5():
    tts_service.speak_to_file("")

def on_ctrl_6():
    tts_service.speak_to_file("")

def on_ctrl_7():
    tts_service.speak_to_file("")

def on_ctrl_8():
    tts_service.speak_to_file("")

def on_ctrl_9():
    tts_service.speak_to_file("这是 ctontrol 9")

keyboard.add_hotkey("ctrl+alt+0", on_ctrl_0)
keyboard.add_hotkey("ctrl+alt+1", on_ctrl_1)
keyboard.add_hotkey("ctrl+alt+2", on_ctrl_2)
keyboard.add_hotkey("ctrl+alt+3", on_ctrl_3)
keyboard.add_hotkey("ctrl+alt+4", on_ctrl_4)
keyboard.add_hotkey("ctrl+alt+5", on_ctrl_5)
keyboard.add_hotkey("ctrl+alt+6", on_ctrl_6)
keyboard.add_hotkey("ctrl+alt+7", on_ctrl_7)
keyboard.add_hotkey("ctrl+alt+8", on_ctrl_8)
keyboard.add_hotkey("ctrl+alt+9", on_ctrl_9)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=pathlib.Path("index.html").read_text('utf-8'), status_code=200)

@app.get("/tts")
def tts(txt: str):
    tts_service.speak_to_file(txt)
    return "OK"

@app.head("/tts")
def head_tts():
    return
