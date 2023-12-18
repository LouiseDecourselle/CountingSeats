import cv2
import cv2.aruco as aruco
import numpy as np
import time
import tkinter as tk
from tkinter import Scale


# Fonction pour appliquer un filtre de netteté
def apply_sharpening_filter(image):
   kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]])
   return cv2.filter2D(image, -1, kernel)


# Fonction pour détecter et dessiner les marqueurs ArUco
def detect_aruco(frame, previous_ids, num_arucos_list, place_names):
   # Convertir l'image en niveaux de gris
   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


   # Appliquer un filtre de netteté à l'image en niveaux de gris
   sharp_gray = apply_sharpening_filter(gray)


   # Initialiser le détecteur de marqueurs ArUco
   aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
   parameters = aruco.DetectorParameters()


   # Détecter les marqueurs
   corners, ids, _ = aruco.detectMarkers(sharp_gray, aruco_dict, parameters=parameters)


   # Afficher le nombre d'ArUcos dans un cadre rouge en haut à droite
   if ids is not None and len(ids) > 0:
       # Filtrer les doublons et afficher le nombre d'ArUcos uniques
       unique_ids = set(ids.flatten())
       num_arucos = len(unique_ids)


       # Associer chaque ID à un nom de place
       for aruco_id in unique_ids:
           place_name = place_names.get(aruco_id, f"Place {aruco_id}")
           cv2.putText(frame, f"{place_name}", (int(corners[0][0][0][0]), int(corners[0][0][0][1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


   else:
       num_arucos = 0


   cv2.rectangle(frame, (10, 10), (250, 50), (0, 0, 255), -1)  # Rectangle rouge
   cv2.putText(frame, f"Seats available: {num_arucos}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)




   # Mettre à jour les IDs précédents
   previous_ids = ids.flatten() if ids is not None else []


   # Ajouter le nombre d'ArUcos à la liste
   num_arucos_list.append(num_arucos)


   return previous_ids


# Fonction appelée lors du changement de la valeur de la jauge
def update_exposure(value):
   value = int(value)
   cap.set(cv2.CAP_PROP_EXPOSURE, value)


# Ouvrir la capture vidéo de la caméra (0 pour la caméra par défaut)
cap = cv2.VideoCapture(0)


# Créer une fenêtre Tkinter pour la jauge d'exposition
root = tk.Tk()
root.title("Exposure Control")


# Créer une échelle (jauge) pour régler l'exposition
exposure_scale = Scale(root, from_=-10, to=10, orient="horizontal", label="Exposure", command=update_exposure)
exposure_scale.pack()


previous_ids = []
num_arucos_list = []


# Dictionnaire associant les identifiants ArUco (IDs) aux noms des places
place_names = {0: "Place 1", 1: "Place 2", 2: "Place 3", 3: "Place 4"}  # Ajoutez autant de places que nécessaire


start_time = time.time()


while True:
   # Lire une image de la caméra
   ret, frame = cap.read()


   # Vérifier si la lecture de l'image est réussie
   if not ret:
       print("Erreur de lecture de l'image.")
       break


   # Appeler la fonction de détection d'ArUco
   previous_ids = detect_aruco(frame, previous_ids, num_arucos_list, place_names)


   # Afficher l'image résultante
   cv2.imshow('ArUco Detection', frame)


   # Afficher la moyenne dans une autre fenêtre toutes les deux secondes
   if time.time() - start_time >= 0.5:
       average_num_arucos = int(np.mean(num_arucos_list))
       window = np.zeros((100, 100), dtype=np.uint8)
       cv2.putText(window, str(average_num_arucos), (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
       cv2.imshow('Average Seats', window)


       # Réinitialiser le temps et la liste pour les deux prochaines secondes
       start_time = time.time()
       num_arucos_list = []


   # Attendre un court instant pour que la fenêtre Tkinter soit mise à jour
   root.update()


   # ...


   # Initialisation de la variable d'état de visibilité
   marker_visible = False
   corners = None
   while True:
       # Lire une image de la caméra
       ret, frame = cap.read()


       # Vérifier si la lecture de l'image est réussie
       if not ret:
           print("Erreur de lecture de l'image.")
           break


       # Appeler la fonction de détection d'ArUco
       previous_ids = detect_aruco(frame, previous_ids, num_arucos_list, place_names)


       # Afficher l'image résultante
       cv2.imshow('ArUco Detection', frame)


       # Afficher la moyenne dans une autre fenêtre toutes les deux secondes
       if time.time() - start_time >= 0.5:
           average_num_arucos = int(np.mean(num_arucos_list))
           window = np.zeros((100, 100), dtype=np.uint8)
           cv2.putText(window, str(average_num_arucos), (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
           cv2.imshow('Average Seats', window)


           # Réinitialiser le temps et la liste pour les deux prochaines secondes
           start_time = time.time()
           num_arucos_list = []


       # Attendre un court instant pour que la fenêtre Tkinter soit mise à jour
       root.update()


       # Vérifier si l'Aruco est détecté
       if any(previous_ids):
           # Mettre à jour l'état de visibilité
           marker_visible = True
       else:
           # Si le marqueur était visible précédemment, afficher toujours le nom de la place
           if marker_visible:
               for aruco_id in previous_ids:
                   place_name = place_names.get(aruco_id, f"Place {aruco_id}")
                   cv2.putText(frame, f"{place_name}", (int(corners[0][0][0][0]), int(corners[0][0][0][1]) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


       # Quitter la boucle si la touche 'q' est enfoncée
       if cv2.waitKey(1) & 0xFF == ord('q'):
           break


   # ...




   # Quitter la boucle si la touche 'q' est enfoncée
   if cv2.waitKey(1) & 0xFF == ord('q'):
       break


# Libérer la capture vidéo, détruire la fenêtre Tkinter et fermer les fenêtres OpenCV
cap.release()
root.destroy()
cv2.destroyAllWindows()


