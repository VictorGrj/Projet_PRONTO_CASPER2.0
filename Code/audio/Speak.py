import pygame
import time
import threading


class Speak(threading.Thread):

    def __init__(self, OUTPUT_PATH):
        super().__init__()
        self._running = True
        self.OUTPUT_PATH = OUTPUT_PATH

    def run(self):
        try:
            self.playAudio(self.OUTPUT_PATH)
        except Exception as e:
            print(f"[SPEAK ERROR] {e}")

    def stop(self):
        self._running = False

    def playAudio(self, audioPath):

        pygame.mixer.init()

        pygame.mixer.music.load(audioPath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if not self._running:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
            
        pygame.mixer.quit()
