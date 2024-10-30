import cv2
import numpy as np

# Funktion zur Überprüfung, ob sich zwei Rechtecke überlappen
def rectangles_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 > x2 + w2 or x2 > x1 + w1 or y1 > y2 + h2 or y2 > y1 + h1)

# Funktion zur Erkennung grüner Objekte und Ausgabe der nummerierten Koordinaten
def detect_green_object(frame):
    # Konvertiere das Bild von BGR zu HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Definiere den Bereich für die Farbe Grün in HSV
    lower_green = np.array([40, 40, 40])  # Untere Grenze für Grün
    upper_green = np.array([80, 255, 255])  # Obere Grenze für Grün

    # Maske erstellen, um nur grüne Bereiche zu erkennen
    mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    # Finde die Konturen des Objekts
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    objects = []  # Liste zur Speicherung von Objekten und deren Positionen

    # Zeichne eine Box um das erkannte grüne Objekt und gib die Koordinaten des Mittelpunkts aus
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 500:  # Filter für zu kleine Bereiche
            x, y, w, h = cv2.boundingRect(contour)
            current_rect = (x, y, w, h)

            # Prüfen, ob das neue Rechteck sich mit vorhandenen Objekten überschneidet
            overlap = False
            for obj_rect in objects:
                if rectangles_overlap(current_rect, obj_rect):
                    overlap = True
                    break

            if not overlap:
                # Wenn kein Überschneidungsfehler vorliegt, füge das Objekt zur Liste hinzu
                objects.append(current_rect)

                # Berechne den Mittelpunkt der Box
                cx, cy = x + w // 2, y + h // 2

                # Nummeriere das Objekt und beschrifte es im Bild
                object_label = f"Objekt #{len(objects)}"
                print(f"{object_label}: X={cx}, Y={cy}")  # Gib die nummerierten Koordinaten aus
                
                # Zeichne das Rechteck und beschrifte es
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, object_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame

# Zugriff auf die Kamera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Fehler beim Öffnen der Kamera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Abrufen des Frames")
        break

    # Erkennung des grünen Objekts
    frame_with_box = detect_green_object(frame)

    # Zeige das Ergebnis
    cv2.imshow('Green Object Detection', frame_with_box)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
