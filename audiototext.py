import requests
import speech_recognition as sr
from pydub import AudioSegment


def convertAudioToText(filename):
    # initialize the recognizer
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        result_list = [text]
        return result_list


def convertTowav(filename):
    # src = "C:\\Users\\DELL\\Desktop\\project\\deep\\adv\\MMcdb3de3668eac02c207dae219cffab39.ogg"
    # dst = "C:\\Users\\DELL\\Desktop\\project\\deep\\adv\\test1.wav"
    src = filename + ".ogg"
    dst = filename + ".wav"
    sound = AudioSegment.from_ogg(src)
    sound.export(dst, format="wav")


def formatAudio(url, msg_id):
    audio_data = requests.get(url).content
    audio_path = "media/" + str(msg_id)
    src = audio_path + ".ogg"
    with open(src, 'wb') as handler:
        handler.write(audio_data)
    convertTowav(audio_path)
    filename = audio_path + ".wav"
    return filename
