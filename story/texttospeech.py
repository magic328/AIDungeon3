# import necessary packages
from google.cloud import texttospeech
import pyaudio
import hashlib
import wave
import os


class TTSEngine:
    def __init__(self, key,
    voiceParams=texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        name="en-GB-Wavenet-B",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )):
        # store Google Cloud key in a system environment variable
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key

        # store voice parameters and audio configuration
        self.voiceParams = voiceParams

        # initialize and store GC TextToSpeech client
        self.client = texttospeech.TextToSpeechClient()


    def generate(self, text):
        return self.client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=text),
                voice=self.voiceParams,
                audio_config=texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16, # wav encoding
                    pitch=-1,
                    speaking_rate=1
                )
            )

    def speak(self, text):
        # initialize variables for audio file caching and playback
        audio_cachefile = "/tmp/tts/%s.wav" % (hashlib.sha256(bytes(str(text), encoding="utf-8")).hexdigest())
        chunk = 1000
        format = pyaudio.paInt16
        channels=1
        bitrate=24000

        # initialize pyaudio and an audio stream
        p = pyaudio.PyAudio()
        stream = p.open(
            format=format,
            rate=bitrate,
            channels=channels,
            output=True,
            frames_per_buffer=chunk
        )

        # to save on API requests (quota), check for the existence of
        # a cache file for this speech, and generate the speech if
        # not exist
        if not os.path.exists(audio_cachefile):
            audio_response = self.generate(text).audio_content
            # cache the speech
            with open(audio_cachefile, 'wb') as f:
                f.write(audio_response)

        # play the speech from the cached file
        wf = wave.open(audio_cachefile, 'rb')
        response = wf.readframes(chunk)
        while len(response) > 0:
            stream.write(response)
            response = wf.readframes(chunk)