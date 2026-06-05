#####################################################################################################################################################
###################################################################### IMPORTS #######################################################################
#####################################################################################################################################################

import RPi.GPIO as GPIO
import sounddevice as sd
import numpy as np
import queue
import wave
import os
import json
from google import genai
import pygame
import time
import subprocess
import threading
from vosk import Model, KaldiRecognizer

class AudioProcessing(threading.Thread):
    """
    This class acquires an audio signal from the raspberry's USB 1 port with sounddevice while the 
    user holds down the pushbutton on GPIO PORT 4. 
    The signal is then converted into a text query for wikipedia thanks to vosk. 
    A text summary of the wikipedia page is then generated, which in turn is converted into an 
    audio file thanks to piper.
    """

    def __init__ (self):
        """
            This function is the constructor of the class.
            In:
                * self:   Reference to the current object.
            Out:
                * A new instance of the class.
        """
        # ---------- initialise parallelism ----------
        super().__init__()
        self._running = True
        self._lock = threading.Lock()
        self.userSpeak = True # True if user is speaking or robot waiting for the question 

        # ---------- Configuration Speech to text ----------
        self.BUTTON_PIN = 4
        self.AUDIO_CHANNEL = 2
        self.INPUT_FILENAME = os.path.join(os.path.dirname(__file__), "..", "audio", "recorded.wav")
        self.MODEL_PATH_STT = os.path.join(os.path.dirname(__file__), "..", "lib", "vosk-model-small-fr-0.22")
        self.q = queue.Queue() #queue of recorded data

        # ---------- Configuration Wikipedia ----------
        self.answer = None
        self.model = Model(self.MODEL_PATH_STT)

        # ---------- Configuration Text to speech ----------
        self.MODEL_PATH_TTS = os.path.join(os.path.dirname(__file__), "..", "lib", "fr_FR-tom-medium.onnx")
        self.PIPER_PATH = os.path.join(os.path.dirname(__file__), "..", "lib", "piper","piper")
        self.OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "audio", "answer.wav")

#############################################################################################################################
#################################################### Thread methods #########################################################
#############################################################################################################################

    def run(self):
        """Main method executed in the thread."""

        self.answer = None
        self.userSpeak = True

        try:
            self.recordingAudio()
            self.userSpeak = False
            query = self.stt()

            print(f"DEBUG: Vosk a compris -> '{query}'")


            if query == "": 
                self.answer = None 
            else:
                self.gemini(query)
                if self.answer != None: 
                    self.tts(self.answer)

        except Exception as e:
            print(f"Error in AudioProcessing thread: {e}")
        finally:
            sd.stop()
            time.sleep(1)

    def stop(self):
        """Stop generating answer """
        self._running = False
    
    def getUserSpeak(self):
        return self.userSpeak

#############################################################################################################################
#################################################### Speech to text #########################################################
#############################################################################################################################

    def callback(self, indata, frames, time_info, status):
        if status:
            print(status)

        self.q.put(indata.copy())

    def recordingAudio(self):
        try:
            SAMPLE_RATE = 16000  

            self.q = queue.Queue()

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            print("DEBUG: attente bouton")

            while GPIO.input(self.BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.01)

            print("DEBUG: enregistrement")

            recorded_frames = []

            # Recherche ReSpeaker
            device_index = None

            for i, device in enumerate(sd.query_devices()):
                name = device['name'].lower()

                if "seeed" in name or "respeaker" in name:
                    device_index = i
                    print(f"DEBUG: ReSpeaker trouvé -> {device['name']}")
                    break

            if device_index is None:
                print("DEBUG: aucun ReSpeaker trouvé")
                print(sd.query_devices())
                return

            sd.stop()
            #sd._terminate()
            #sd._initialize()
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,          # MONO DIRECTEMENT
                dtype='int16',
                blocksize=8000,
                device=device_index,
                callback=self.callback
            )

            stream.start()

            while GPIO.input(self.BUTTON_PIN) == GPIO.LOW:
                try:
                    data = self.q.get(timeout=0.1)
                    recorded_frames.append(data)

                except queue.Empty:
                    pass

            print("DEBUG: fin enregistrement")

            stream.stop()
            stream.close()
            sd.stop()

            time.sleep(1)

            if len(recorded_frames) == 0:
                print("DEBUG: aucun son enregistré")
                return

            recorded_data = np.concatenate(recorded_frames, axis=0)

            # mono
            recorded_data = recorded_data.flatten()

            with wave.open(self.INPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)

                wf.writeframes(recorded_data.tobytes())

            print("DEBUG: WAV sauvegardé")

        except Exception as e:
            print(f"Error in recordingAudio method: {e}")


    def stt(self):
        try:
            if not os.path.exists(self.INPUT_FILENAME):
                return ""
            
            with wave.open(self.INPUT_FILENAME, "rb") as wf:
                # On utilise la fréquence réelle du fichier
                recognizer = KaldiRecognizer(self.model, wf.getframerate())
                
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if recognizer.AcceptWaveform(data):
                        partial = json.loads(recognizer.Result())
                        if partial.get("text", ""):
                            print(f"DEBUG Partiel: {partial['text']}")

            # Résultat final
            result = json.loads(recognizer.FinalResult())
            final_text = result.get("text", "")
            return final_text

        except Exception as e:
            print(f"Error in stt method: {e}")
            return ""

#############################################################################################################################
#################################################### Wikipedia ##############################################################
#############################################################################################################################

    def gemini(self, question):
        client = genai.Client(api_key="AQ.Ab8RN6KfyYLQeEGaFHnz4DrYGJV5_tV8FQXfC0jBs5j4K4qBng")
        try :
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite", 
                contents=f"Réponds en une phrases maximum, sans mettre de mot en gras : {question}"
            )
            self.answer = response.text
            print(f"Gemini a répondu : {self.answer}")
        except Exception as e:
            print(f"Error in gemini method : {e}")
            self.answer = "Désolé, je n'ai pas pu accéder à mon cerveau."

    def getAnswer(self):
        return self.answer


#############################################################################################################################
#################################################### Text to speech #########################################################
#############################################################################################################################
    def tts(self, text:str):
        """
            This function generates an audio file of the robot's answer.
            In:
                * self : Reference to the current object.
                * text : the text answer
            Out:
                * A summary of the wikipedia page
        """
        # Define the command to call Piper
        piper_command = [
            self.PIPER_PATH, "--model", self.MODEL_PATH_TTS,"--output_file", self.OUTPUT_PATH]

        # Call Piper via subprocess
        subprocess.run(
        piper_command,
        input=text.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
