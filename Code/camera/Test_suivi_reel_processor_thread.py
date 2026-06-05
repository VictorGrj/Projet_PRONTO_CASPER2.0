import cv2
import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Queue
import threading

# ====== SERVO SETUP ======
SERVO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(7.5)

def set_angle(angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)

# ====== PARAMETERS ======
min_angle = 30
max_angle = 150
deadzone = 50 #zone neutre - assure la convergence du modele
k = 0.03 #proportional gain
damping = 0.8
pixels_par_degre = 640 / 60  # fait la transaction degree to pixel

# ====== CAMERA PROCESS ======
def camera_process(angle_queue):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("Caméra non détectée")
        return
    height, width = frame.shape[:2]
    center_x = width // 2
    face_center_smoothed = center_x
    angle = 90

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            x, y, w, h = faces[0]  # on suit le premier visage détecté
            face_center_x = x + w // 2
            face_center_smoothed = 0.8 * face_center_smoothed + 0.2 * face_center_x

            virtual_center = center_x + angle * pixels_par_degre
            error = face_center_smoothed - virtual_center

            if abs(error) > deadzone:
                prev_angle = angle
                angle += k * error
                angle = angle * damping + prev_angle * (1 - damping)

            angle = max(min_angle, min(max_angle, angle))

            # Envoi de l’angle à la queue
            if not angle_queue.full():
                angle_queue.put(angle)

    cap.release()

# ====== SERVO THREAD ======
def servo_thread(angle_queue):
    while True:
        if not angle_queue.empty():
            angle = angle_queue.get()
            set_angle(angle)
        time.sleep(0.02)  # petit délai pour ne pas saturer le CPU

# ====== MAIN ======
if __name__ == "__main__":
    angle_queue = Queue(maxsize=1)  # On fixe la taille de la Queue à 1 afin de toujours garder le dernier angle
    #On évite ainsi les problèmes dus à des potentiels retards provenant du thread ou du processeur et le tout est plus fluide
    # Lancement du thread servo
    t = threading.Thread(target=servo_thread, args=(angle_queue,), daemon=True)
    t.start()
    # Lancement du process caméra
    p = Process(target=camera_process, args=(angle_queue,))
    p.start()
    p.join()

    pwm.stop()
    GPIO.cleanup()