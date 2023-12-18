import cv2
import tkinter as tk
from PIL import Image, ImageTk
import cv2.aruco as aruco
import numpy as np
import time
import pygame.mixer
from tkinter import Scale


class WebcamApp:
   blanc = True
   rouge = False


   def __init__(self, fenetre, titre):
       self.btn_rouge_image_tk = None


       self.fenetre = fenetre
       self.fenetre.title(titre)


       # Initialisation de la webcam avec OpenCV
       self.cap = cv2.VideoCapture(0)
       _, self.frame = self.cap.read()


       # Définir les paramètres pour l'enregistrement vidéo
       fourcc = cv2.VideoWriter_fourcc(*'XVID')
       self.output_file = 'C:/Users/pauln/PycharmProjects/pythonProject/webcam_video.avi'
       self.fps = 30.0
       self.resolution = (640, 480)


       # Créer l'objet VideoWriter
       self.out = cv2.VideoWriter(self.output_file, fourcc, self.fps, self.resolution)


       # Chargement de l'image sans redimensionnement
       self.logo_image = Image.open("logoMTA.png")
       self.logo_image = ImageTk.PhotoImage(self.logo_image)


       # Chargement des images du bouton
       self.btn_blanc_image = Image.open("btnBlanc.png")
       self.btn_rouge_image = Image.open("btnRoouge.png")


       # Création du canevas pour superposer le logo, la vidéo, le texte et le bouton
       self.canevas = tk.Canvas(fenetre, width=self.cap.get(3), height=self.cap.get(4))
       self.canevas.pack()


       # Création de l'image du logo en haut à gauche sur le canevas
       self.logo_id = self.canevas.create_image(10, 10, anchor=tk.NW, image=self.logo_image)


       # Création de l'image de la vidéo sur le canevas
       self.video_id = self.canevas.create_image(0, 0, anchor=tk.NW)


       # Ajout du texte en bas à gauche avec une taille de police plus grande
       self.places_text_id = self.canevas.create_text(10, self.cap.get(4)-10, anchor=tk.SW, text="Places available: 0",
                                                      fill="white", font=("Helvetica", 30, "bold"))


       # Création du bouton au centre bas de la vidéo
       self.btn_blanc_image_tk = ImageTk.PhotoImage(self.btn_blanc_image)
       self.btn_rouge_image_tk = ImageTk.PhotoImage(self.btn_rouge_image)
       self.btn_blanc_id = self.canevas.create_image(self.cap.get(3)/2, self.cap.get(4)-50, anchor=tk.S, image=self.btn_blanc_image_tk)


       # Booléen pour suivre l'état du bouton rouge
       self.bouton_rouge_visible = False


       # Variables pour la détection ArUco
       self.previous_ids = []
       self.num_arucos_list = []
       self.start_time = time.time()
       self.alarm_start_time = None


       # Mise à jour du canevas avec la vidéo de la webcam
       self.mise_a_jour_video()


       # Lancement de la boucle principale de la fenêtre
       self.fenetre.mainloop()


   def mise_a_jour_video(self):
       _, frame = self.cap.read()
       frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       img = Image.fromarray(frame)
       img = ImageTk.PhotoImage(img)


       # Enregistrer l'image dans le fichier vidéo
       self.out.write(frame)


       # Mettre à jour l'image de la vidéo sur le canevas
       self.canevas.itemconfig(self.video_id, image=img)


       # Déplacer la vidéo derrière le logo
       self.canevas.tag_lower(self.video_id, self.logo_id)


       # Mettre à jour le texte avec la variable places
       places = 0  # Mettez la valeur souhaitée ici
       self.canevas.itemconfig(self.places_text_id, text=f"Places available: {self.detect_aruco(frame, self.previous_ids, self.num_arucos_list)}")


       # Mettre à jour le bouton pour qu'il appelle la fonction action_du_bouton
       self.canevas.tag_bind(self.btn_blanc_id, "<Button-1>", lambda event: self.action_du_bouton())


       # Appeler la fonction de détection ArUco
       self.previous_ids = self.detect_aruco(frame, self.previous_ids, self.num_arucos_list)


       # Vérifier si le nombre d'ArUcos est
       if np.mean(self.num_arucos_list) == 0:
           if self.alarm_start_time is None:
               self.alarm_start_time = time.time()
           elif time.time() - self.alarm_start_time >= 5:
               self.handle_alarm()
               self.alarm_start_time = None
       else:
           self.alarm_start_time = None


       # Afficher la moyenne dans une autre fenêtre toutes les deux secondes
       if time.time() - self.start_time >= 0.5:
           average_num_arucos = int(np.mean(self.num_arucos_list))
           window = np.zeros((100, 100), dtype=np.uint8)
           cv2.putText(window, str(average_num_arucos), (25, 65), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
           cv2.imshow('Average Seats', window)


           # Réinitialiser le temps et la liste pour les deux prochaines secondes
           self.start_time = time.time()
           self.num_arucos_list = []


       self.canevas.img = img  # Garder une référence pour éviter la suppression par le garbage collector
       self.canevas.after(10, self.mise_a_jour_video)


   def action_du_bouton(self):
       self.bouton_rouge_visible = not self.bouton_rouge_visible


       if self.bouton_rouge_visible:
           # Afficher le bouton rouge
           self.canevas.itemconfig(self.btn_blanc_id, image=self.btn_rouge_image_tk)
       else:
           # Cacher le bouton rouge
           self.canevas.itemconfig(self.btn_blanc_id, image=self.btn_blanc_image_tk)


   def detect_aruco(self, frame, previous_ids, num_arucos_list):
       # Convertir l'image en niveaux de gris
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


       # Appliquer un filtre de netteté à l'image en niveaux de gris
       sharp_gray = self.apply_sharpening_filter(gray)


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
       else:
           num_arucos = 0


       cv2.rectangle(frame, (10, 10), (250, 50), (0, 0, 255), -1)  # Rectangle rouge
       cv2.putText(frame, f"Seats available: {num_arucos}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


       # Mettre à jour les IDs précédents
       previous_ids = ids.flatten() if ids is not None else []


       # Ajouter le nombre d'ArUcos à la liste
       num_arucos_list.append(num_arucos)


       return num_arucos


   def apply_sharpening_filter(self, image):
       kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]])
       return cv2.filter2D(image, -1, kernel)


   def handle_alarm(self):
       # Jouer le son d'alarme
       pygame.mixer.init()
       alarm_sound = pygame.mixer.Sound("sondurgence.wav")
       alarm_sound.play()


   def __del__(self):
       # Libérer la capture vidéo, l'objet VideoWriter, détruire la fenêtre Tkinter et fermer les fenêtres OpenCV
       self.cap.release()
       self.out.release()
       cv2.destroyAllWindows()




if __name__ == "__main__":
   root = tk.Tk()
   app = WebcamApp(root, "Application Webcam")
   root.mainloop()
