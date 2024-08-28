from gtts.lang import tts_langs
from gtts import gTTS
import os

print(tts_langs())

text = "tyoskennella"
language = "fi"

tts = gTTS(text=text, lang=language)
tts.save("test_finnish.mp3")

os.system("start test_finnish.mp3")  # For Windows