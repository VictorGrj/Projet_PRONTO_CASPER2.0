import RPi.GPIO as GPIO
import time
from adafruit_servokit import ServoKit
import threading


class Servo(threading.Thread):
    def __init__(self, servoName, kit=None):
        super().__init__()

        self.servoName = servoName
        self.kit = kit

        self.running = True

        self.OE_PIN = 17
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.OE_PIN, GPIO.OUT)
        GPIO.output(self.OE_PIN, GPIO.LOW)

        self.PIN_PINCE_DROITE = 3
        self.PIN_PINCE_GAUCHE = 7

        self.PINCE_OUVERTE = 10
        self.PINCE_FERMEE = 70

        # ✅ POINT 5 ICI (INITIALISATION PINCES)
        self.kit.servo[self.PIN_PINCE_DROITE].angle = self.PINCE_OUVERTE
        self.kit.servo[self.PIN_PINCE_GAUCHE].angle = self.PINCE_OUVERTE
        time.sleep(0.3)

    # ---------------- THREAD MAIN ----------------
    def run(self):
        try:
            if self.servoName == "rightArm":
                self.arm_with_claw(arm_pin=0, claw_pin=self.PIN_PINCE_DROITE, direction=1)

            elif self.servoName == "leftArm":
                self.arm_with_claw(arm_pin=2, claw_pin=self.PIN_PINCE_GAUCHE, direction=-1)

            elif self.servoName == "head":
                self.look_around(pin=1)

        except Exception as e:
            print(f"[Servo ERROR] {e}")

        finally:
            self.stop_servos()
            GPIO.output(self.OE_PIN, GPIO.HIGH)

    # ---------------- ARM + CLAW SYNCHRO ----------------
    def set_claw(self, claw_pin, angle):
        self.kit.servo[claw_pin].angle = angle
        time.sleep(0.15)

    def open_claw(self, claw_pin):
        self.set_claw(claw_pin, self.PINCE_OUVERTE)

    def close_claw(self, claw_pin):
        self.set_claw(claw_pin, self.PINCE_FERMEE)

    def arm_with_claw(self, arm_pin, claw_pin, direction):
        speed = 0.5 * direction

        # sécurité : pince ouverte avant mouvement
        self.open_claw(claw_pin)

        time.sleep(0.2)

        # avance bras
        self.kit.continuous_servo[arm_pin].throttle = speed
        time.sleep(0.5)

        # attraper objet
        self.close_claw(claw_pin)
        time.sleep(0.3)

        # stop bras
        self.kit.continuous_servo[arm_pin].throttle = 0
        time.sleep(0.2)

        # retour bras
        self.kit.continuous_servo[arm_pin].throttle = -speed
        time.sleep(0.5)

        self.kit.continuous_servo[arm_pin].throttle = 0

        # relâchement léger
        self.open_claw(claw_pin)

    # ---------------- HEAD ----------------
    def look_around(self, pin):
        self.kit.continuous_servo[pin].throttle = 0.2
        time.sleep(0.4)

        self.kit.continuous_servo[pin].throttle = -0.2
        time.sleep(0.4)

        self.kit.continuous_servo[pin].throttle = 0

    # ---------------- STOP CLEAN ----------------
    def stop_servos(self):
        try:
            if self.kit:
                for i in range(16):
                    try:
                        self.kit.continuous_servo[i].throttle = 0
                    except:
                        pass
        except:
            pass

    def stop(self):
        self.running = False
        self.stop_servos()
