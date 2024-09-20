import cv2
import os
from tqdm import tqdm
import time
from pystyle import *

System.Title("Gothcam - THE BEST FILTER")
System.Clear()
Cursor.HideCursor()

banner = """
  ▄████  ▒█████  ▄▄▄█████▓ ██░ ██  ▄████▄   ▄▄▄       ███▄ ▄███▓
 ██▒ ▀█▒▒██▒  ██▒▓  ██▒ ▓▒▓██░ ██▒▒██▀ ▀█  ▒████▄    ▓██▒▀█▀ ██▒
▒██░▄▄▄░▒██░  ██▒▒ ▓██░ ▒░▒██▀▀██░▒▓█    ▄ ▒██  ▀█▄  ▓██    ▓██░
░▓█  ██▓▒██   ██░░ ▓██▓ ░ ░▓█ ░██ ▒▓▓▄ ▄██▒░██▄▄▄▄██ ▒██    ▒██ 
░▒▓███▀▒░ ████▓▒░  ▒██▒ ░ ░▓█▒░██▓▒ ▓███▀ ░ ▓█   ▓██▒▒██▒   ░██▒
 ░▒   ▒ ░ ▒░▒░▒░   ▒ ░░    ▒ ░░▒░▒░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ░  ░
  ░   ░   ░ ▒ ▒░     ░     ▒ ░▒░ ░  ░  ▒     ▒   ▒▒ ░░  ░      ░
░ ░   ░ ░ ░ ░ ▒    ░       ░  ░░ ░░          ░   ▒   ░      ░   
      ░     ░ ░            ░  ░  ░░ ░            ░  ░       ░   
                                  ░                             
"""
print("\n")
centered_box = Center.XCenter(banner)
Write.Print(centered_box, Colors.dark_gray, interval=0)
print("\n"), print("\n")

# Fonction pour simuler une tâche avec une barre de chargement et un timer
def initialisation_tache(description, etapes):
    pbar = tqdm(total=len(etapes), desc=description)
    for etape in etapes:
        etape()
        pbar.update(1)
    pbar.close()

# Étapes d'initialisation
def charger_haarcascade():
    global face_cascade
    haarcascade_path = r'haarcascades\\haarcascade_frontalface_default.xml'
    if not os.path.exists(haarcascade_path):
        raise FileNotFoundError(f"Le fichier haarcascade_frontalface_default.xml est introuvable à l'emplacement : {haarcascade_path}")
    face_cascade = cv2.CascadeClassifier(haarcascade_path)

def charger_filtre():
    global filter_img
    filter_path = 'filter.png'
    if not os.path.exists(filter_path):
        raise FileNotFoundError(f"Le fichier filter.png est introuvable à l'emplacement : {filter_path}")
    filter_img = cv2.imread(filter_path, cv2.IMREAD_UNCHANGED)
    if filter_img is None:
        raise ValueError(f"Erreur lors du chargement de l'image filter.png")

def ouvrir_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise ValueError("Erreur lors de l'ouverture de la webcam")
    print(Colorate.Color(Colors.blue, "Webcam ouverte avec succès", True))

# Afficher un message stylisé pour le démarrage
print(Colorate.Color(Colors.yellow, "Initialisation du programme...", True))

# Initialisation des ressources avec une barre de chargement
etapes_initialisation = [charger_haarcascade, charger_filtre, ouvrir_webcam]
initialisation_tache("Initialisation des ressources", etapes_initialisation)

# Afficher un timer pour montrer que le programme n'est pas figé
print(Colorate.Color(Colors.blue, "Initialisation terminée. Lancement de la capture vidéo...", True))

System.Clear()

print("\n")
centered_box = Center.XCenter(banner)
Write.Print(centered_box, Colors.dark_gray, interval=0)
print("\n"), print("\n")

print(Colorate.Color(Colors.yellow, "Bienvenue dans GOTHCAM ! Les filtres sont prêts à être appliqués.", True))
print("\n")

for i in tqdm(range(10), desc="Démarrage de la capture vidéo"):
    time.sleep(0.1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erreur lors de la lecture de la frame")
        break

    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détecter les visages avec des paramètres ajustés
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # Ajustez ce paramètre pour plus ou moins de sensibilité
        minNeighbors=8,    # Augmentez ce paramètre pour réduire les faux positifs
        minSize=(50, 50),  # Ajustez la taille minimale des visages à détecter
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        # Agrandir le filtre à une taille plus grande que le visage détecté
        scale_factor = 1.5  # Facteur d'agrandissement
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        filter_resized = cv2.resize(filter_img, (new_w, new_h))

        # Calculer les nouvelles coordonnées pour centrer le filtre agrandi
        x_offset = x - (new_w - w) // 2
        y_offset_adjustment = int(h * 0.25)  # Ajustement vertical pour aligner les yeux
        y_offset = y - (new_h - h) // 2 - y_offset_adjustment

        # Assurez-vous que les coordonnées sont dans les limites de l'image
        if x_offset < 0:
            x_offset = 0
        if y_offset < 0:
            y_offset = 0
        if x_offset + new_w > frame.shape[1]:
            new_w = frame.shape[1] - x_offset
        if y_offset + new_h > frame.shape[0]:
            new_h = frame.shape[0] - y_offset

        # Ajouter le filtre sur le visage détecté
        for c in range(0, 3):
            frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] = filter_resized[:new_h, :new_w, c] * (filter_resized[:new_h, :new_w, 3] / 255.0) + frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] * (1.0 - filter_resized[:new_h, :new_w, 3] / 255.0)

    # Afficher le résultat
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
print("Programme terminé")