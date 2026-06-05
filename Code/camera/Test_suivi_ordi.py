import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur : caméra non détectée")
    exit()

print("Appuie sur 'q' pour quitter")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    height, width = frame.shape[:2]
    center_x = width // 2

    direction = "Aucun visage"

    for (x, y, w, h) in faces:
        face_center_x = x + w // 2

        # Zone morte
        deadzone = 50

        if face_center_x < center_x - deadzone:
            direction = "Droite"
        elif face_center_x > center_x + deadzone:
            direction = "Gauche"
        else:
            direction = "Centre"


        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        break

    print("\rDirection :", direction, end="")

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
