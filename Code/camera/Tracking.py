import cv2
import threading
import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from picamera2 import Picamera2

class CameraTracking(threading.Thread):
    def __init__(self):
        super().__init__()
        self._running = False
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self.BUTTON_PIN = 4 #
        self.head_idx = 1   #
        self.OE_PIN = 17    #
        
        try:
            self.kit = ServoKit(channels=16)
        except Exception as e:
            print(f"ERROR I2C: {e}")
            self.kit = None

        print("LOG: Initialisation du Camera Module 3...")
        try:
            self.picam = Picamera2()
            config = self.picam.create_video_configuration(main={'size': (320, 240), 'format': 'RGB888'})
            self.picam.configure(config)
            
            # --- CORRECTION FOCUS POUR CAMÉRA MODULE 3 ---
            # Mode 2 = Autofocus Continu (la caméra ajuste sa netteté tout le temps)
            self.picam.set_controls({"AfMode": 2}) 
            
            self.picam.start()
            print("LOG: Picamera2 prête avec Autofocus Continu !")
        except Exception as e:
            print(f"ERROR CAMERA: {e}")
            self.picam = None

    def run(self):
        self._running = True
        DEADZONE = 5.0  
        
        smooth_error = 0.0
        lost_face_count = 0 
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.OE_PIN, GPIO.OUT)

        while self._running:
            try:
                if GPIO.input(self.BUTTON_PIN) == GPIO.HIGH and self.picam:
                    frame = self.picam.capture_array()
                    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    
                    # --- PARAMÈTRES OPENCV ---
                    faces = self.face_cascade.detectMultiScale(
                        gray, 
                        scaleFactor=1.05,   
                        minNeighbors=2,     
                        minSize=(25, 25)    
                    )

                    if len(faces) > 0:
                        lost_face_count = 0
                        GPIO.output(self.OE_PIN, GPIO.LOW) #
                        
                        (x, y, w, h) = faces[0]
                        face_center_x = x + (w // 2)
                        raw_error = (face_center_x - 160) / 160
                        
                        # Suivi direct et nerveux pour valider la mécanique
                        smooth_error = (smooth_error * 0.4) + (raw_error * 0.6)
                        angle_approx = smooth_error * 30 
                        
                        print(f"\r[Vision] Visage trouvé ! Angle: {angle_approx:.1f}° | Taille face: {w}x{h}px", end="")

                        if self.kit:
                            try:
                                if abs(angle_approx) > DEADZONE:
                                    # Vitesse de base franche pour vaincre le poids de la tête
                                    speed = 0.24 + (abs(smooth_error) * 0.15)
                                    speed = min(speed, 0.45) 
                                    
                                    self.kit.continuous_servo[self.head_idx].throttle = speed if smooth_error > 0 else -speed
                                else:
                                    self.kit.continuous_servo[self.head_idx].throttle = 0
                            except Exception as i2c_err:
                                print(f"\n[I2C Moteur Error]: {i2c_err}")
                    else:
                        lost_face_count += 1
                        if lost_face_count > 4:
                            if self.kit:
                                try: self.kit.continuous_servo[self.head_idx].throttle = 0
                                except: pass
                else:
                    if self.kit:
                        try: self.kit.continuous_servo[self.head_idx].throttle = 0
                        except: pass
                        
            except Exception as loop_err:
                print(f"\n[Tracking Loop Error]: {loop_err}")
            
            time.sleep(0.04)

        if self.picam:
            self.picam.stop()
            self.picam.close()
        if self.kit:
            try: self.kit.continuous_servo[self.head_idx].throttle = 0
            except: pass
        GPIO.output(self.OE_PIN, GPIO.HIGH) #

    def stop(self):
        self._running = False