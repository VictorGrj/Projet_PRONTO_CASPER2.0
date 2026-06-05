################################################################################################################################
################################################# IMPORTS ######################################################################
################################################################################################################################
# ---------- Audio ----------
from audio.AudioProcessing import AudioProcessing as Audio
from audio.Speak import Speak

# ---------- Screen ----------
from screen.Screen import Screen
import pygame

# ---------- Servo ----------
from servo.Servo import Servo
from adafruit_servokit import ServoKit

# ---------- Camera Tracking ----------
from camera.Tracking import CameraTracking

# ---------- Others ----------
import time
import os

class Main:
    """
    Cette classe principale orchestre l'ensemble des threads pour faire interagir le robot avec l'utilisateur.
    """

    def __init__(self):
        "Constructeur de la classe"
        self.running = True

        # Écran (Thread permanent)
        self.screen = Screen(mode="speaking")
        self.screen.start()
        
        # Suivi de tête (Thread permanent)
        self.tracker = CameraTracking()
        self.kit = ServoKit(channels=16)
        self.kit.servo[3].angle = 10
        self.kit.servo[7].angle = 10

    def start(self):
        """Gestionnaire d'événements et boucle principale."""

        print("START robot")
        self.tracker.start()

        try:
            # -------- Introduction (hello/tuto) --------
            OUTPUT_PATH = os.path.join(os.path.dirname(__file__), ".", "audio", "preRecordedDialogs","hello.wav")
            audioHello = Speak(OUTPUT_PATH)
            servoR = Servo("rightArm", self.kit)
            servoL = Servo("leftArm", self.kit)

            audioHello.start()
            servoR.start()
            servoL.start()

            # Attente stricte de la fin de l'intro
            while self.running:
                if not audioHello.is_alive():
                    audioHello.stop()
                    servoR.stop()
                    servoL.stop()
                    self.running = False
                time.sleep(0.1)

            # --- Pause de sécurité pour la carte audio ---
            time.sleep(0.5)

            # -------- BOUCLE PRINCIPALE DE DIALOGUE --------
            while True:
                try: 
                    self.running = True

                    self.screen.change_mode("speaking")
                    OUTPUT_PATH = os.path.join(os.path.dirname(__file__), ".", "audio", "preRecordedDialogs","youCanSpeak.wav")
                    audioYouCanSpeak = Speak(OUTPUT_PATH)
                    
                    audioYouCanSpeak.start()
                    audioYouCanSpeak.join() # On attend impérativement qu'il finisse de parler
                    audioYouCanSpeak.stop()
                    
                    # On laisse 0.5s à Linux pour relâcher complètement la carte son
                    time.sleep(0.5)
                    
                    # 2. Le robot écoute -> Mode waiting
                    self.screen.change_mode("waiting")
                    audio = Audio()
                    audio.start()

                    while self.running:
                        # Passage en mode "thinking" dès que l'utilisateur relâche le bouton
                        if not audio.getUserSpeak():
                            self.screen.change_mode("thinking")

                        # Fin du traitement Vosk + Gemini
                        if not audio.is_alive():
                            audio.stop()
                            audio.join()
                            self.running = False

                        time.sleep(0.1)

                    # -------- 3. PHASE DE PAROLE & MOUVEMENT DES BRAS --------
                    self.running = True
                    print("getAnswer=", audio.getAnswer())
                    
                    if audio.getAnswer() is None:  # CAS 1 : Le robot ne sait pas
                        self.screen.change_mode("speaking")
                        OUTPUT_PATH = os.path.join(os.path.dirname(__file__), ".", "audio", "preRecordedDialogs","dontKnow.wav")
                        speak_task = Speak(OUTPUT_PATH)
                        
                        # On instancie la tête ET les bras
                        servoH = Servo("head", self.kit)
                        servoR = Servo("rightArm", self.kit)
                        servoL = Servo("leftArm", self.kit)

                        speak_task.start()
                        servoH.start()
                        servoR.start()
                        servoL.start()

                        while self.running:
                            if not speak_task.is_alive():
                                speak_task.stop()
                                servoH.stop()
                                servoR.stop()
                                servoL.stop()
                                self.running = False
                            time.sleep(0.1)

                    else:  # CAS 2 : Le robot répond (Gemini)
                        self.screen.change_mode("teaching")
                        OUTPUT_PATH = os.path.join(os.path.dirname(__file__), ".", "audio", "answer.wav")
                        speak_task = Speak(OUTPUT_PATH)
                        
                        # On instancie les deux bras
                        servoR = Servo("rightArm", self.kit)
                        servoL = Servo("leftArm", self.kit)
                        
                        speak_task.start()
                        servoR.start()
                        servoL.start()

                        while self.running:
                            if not speak_task.is_alive():
                                speak_task.stop()
                                servoR.stop()
                                servoL.stop()
                                self.running = False
                            time.sleep(0.1)
                    
                    # Petite pause avant de relancer le cycle complet
                    time.sleep(0.5)

                except OSError as err:
                    # Si le suivi de visage et les bras rentrent en collision sur l'I2C, 
                    # on intercepte l'erreur pour que le script ne s'éteigne pas 
                    print(f"\n[I2C IGNORED] Micro-coupure du bus I2C ({err}). Le robot respire et continue !\n")
                    time.sleep(0.5)
                    self.running = False 
                    continue

        except Exception as e:
            print(f"Error in the main event loop: {e}")
            self.tracker.stop()

if __name__ == "__main__":
    robot = Main()
    robot.start()
