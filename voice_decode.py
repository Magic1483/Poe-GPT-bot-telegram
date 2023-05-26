import speech_recognition as speech_recog
from pydub import AudioSegment
import os

def ogg2wav(ofn):
    wfn = ofn.replace('.ogg','.wav')
    x = AudioSegment.from_file(ofn)
    x.export(wfn, format='wav')    # maybe use original resolution to make smaller

def voice_decode():
	ogg2wav('downloads/voice.ogg')
	os.remove('downloads/voice.ogg')

	audio = speech_recog.AudioFile('downloads/voice.wav')
	r= speech_recog.Recognizer()

	with audio as audio_file:
		audio_content = r.record(audio_file)


	text = r.recognize_google(audio_content,language="ru-RU")
	os.remove('downloads/voice.wav')

	return text

