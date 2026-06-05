import cv2
import RPi.GPIO as GPIO
import time

# ====== SERVO SETUP ======
SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz
pwm.start(7.5)  # Position neutre

#To set the new position of the angle
def set_angle(angle):
    duty = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.02)

angle = 90  # position initiale

# ====== OPENCV ======
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur : caméra non détectée")
    exit()

print("Appuie sur 'q' pour quitter")


ret, frame = cap.read()
height, width = frame.shape[:2]
center_x = width // 2 #real center of the camera
actual_center = center_x #virtual center of the camera (after a movement of x degrees by the servos)
deadzone = 50 #limit of the stability of the system (pixels)
k = 0.05 #proportionnal gain
pixels_par_degre = width / 60 # how to pass from degree to pixels
face_center_x_smoothed = center_x #damping

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)


    direction = "Aucun visage"


    for (x, y, w, h) in faces:
        #damping
        face_center_x = x + w // 2
        face_center_x_smoothed = 0.8 * face_center_x_smoothed + 0.2 * face_center_x
        face_center_x_previous = face_center_x_smoothed

        actual_center = center_x + angle * pixels_par_degre
        error = face_center_x_smoothed - actual_center #error

        if abs(error) > deadzone:
            #Modification de la valeur de l'angle avec damping
            previous_angle = angle
            angle += k * error
            angle = angle * 0.95 + previous_angle * 0.05

            #Tests pour le debogage
            if error < 0:
                direction = "Droite"
            else:
                direction = "Gauche"
        else:
            direction = "Centre"


        angle = max(30, min(150, angle))
        set_angle(angle)

        #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        break

    print("\rDirection :", direction, "Angle:", angle, end="")

    #cv2.imshow("Camera", frame)

    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

cap.release()
pwm.stop()
GPIO.cleanup()
cv2.destroyAllWindows()