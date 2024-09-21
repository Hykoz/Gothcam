import cv2
import os
import threading
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import ctypes

# Configuration de la fenêtre principale avec ttkthemes
root = ThemedTk(theme="blue")
root.title("Gothcam - Become Batman.")
root.configure(bg='#242424')

# Texte ASCII
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

# Affichage du texte ASCII
ascii_label = tk.Label(root, text=banner, font=("Courier", 10), bg='#242424', fg='#c4d0d6')
ascii_label.pack()

# Canevas pour afficher la vidéo
canvas = tk.Canvas(root, width=640, height=480, bg='#242424')
canvas.pack()

# Barre de chargement
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=10)

# Variable de contrôle pour l'initialisation
initialisation_terminee = False

# Fonction pour simuler une tâche avec une barre de chargement
def initialisation_tache(description, etapes):
    global initialisation_terminee
    progress["maximum"] = len(etapes)
    for i, etape in enumerate(etapes):
        etape()
        progress["value"] = i + 1
        root.update_idletasks()
    initialisation_terminee = True

# Étapes d'initialisation
def charger_haarcascade():
    global face_cascade
    haarcascade_path = r'haarcascades\\haarcascade_frontalface_default.xml'
    if not os.path.exists(haarcascade_path):
        raise FileNotFoundError(f"Le fichier haarcascade_frontalface_default.xml est introuvable à l'emplacement : {haarcascade_path}")
    face_cascade = cv2.CascadeClassifier(haarcascade_path)
    print("Haarcascade chargé avec succès.")

def charger_filtre():
    global filter_img
    filter_path = 'filter.png'
    if not os.path.exists(filter_path):
        raise FileNotFoundError(f"Le fichier filter.png est introuvable à l'emplacement : {filter_path}")
    filter_img = cv2.imread(filter_path, cv2.IMREAD_UNCHANGED)
    if filter_img is None:
        raise ValueError(f"Erreur lors du chargement de l'image filter.png")
    print("Filtre chargé avec succès.")

def ouvrir_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise ValueError("Erreur lors de l'ouverture de la webcam")
    print("Webcam ouverte avec succès.")

# Initialisation des ressources avec une barre de chargement
etapes_initialisation = [charger_haarcascade, charger_filtre, ouvrir_webcam]
threading.Thread(target=initialisation_tache, args=("Initialisation des ressources", etapes_initialisation)).start()

# Fonction pour capturer et afficher la vidéo
def afficher_video():
    if not initialisation_terminee:
        root.after(10, afficher_video)
        return

    try:
        ret, frame = cap.read()
        if not ret:
            print("Erreur lors de la lecture de la frame")
            return

        # Convertir l'image en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Détecter les visages avec des paramètres ajustés
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=8,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            scale_factor = 1.5
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            filter_resized = cv2.resize(filter_img, (new_w, new_h))

            x_offset = x - (new_w - w) // 2
            y_offset_adjustment = int(h * 0.25)
            y_offset = y - (new_h - h) // 2 - y_offset_adjustment

            if x_offset < 0:
                x_offset = 0
            if y_offset < 0:
                y_offset = 0
            if x_offset + new_w > frame.shape[1]:
                new_w = frame.shape[1] - x_offset
            if y_offset + new_h > frame.shape[0]:
                new_h = frame.shape[0] - y_offset

            for c in range(0, 3):
                frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] = filter_resized[:new_h, :new_w, c] * (filter_resized[:new_h, :new_w, 3] / 255.0) + frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w, c] * (1.0 - filter_resized[:new_h, :new_w, 3] / 255.0)

        # Convertir l'image pour tkinter
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        canvas.imgtk = imgtk

    except Exception as e:
        print(f"Erreur lors de l'affichage de la vidéo : {e}")

    # Appeler cette fonction à nouveau après 10 ms
    root.after(10, afficher_video)

# Démarrer l'affichage de la vidéo
afficher_video()

# Fonction pour fermer proprement l'application
def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()