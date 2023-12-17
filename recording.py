import cv2
import numpy as np
import pygetwindow as gw
import pyautogui

# Récupérer la taille de l'écran principal
screen = gw.getWindowsWithTitle(gw.getActiveWindow().title)[0]
screen_width, screen_height = screen.width, screen.height

# Paramètres pour l'enregistrement vidéo
output_file = "essai1.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = 20
video_writer = cv2.VideoWriter(output_file, fourcc, fps, (screen_width, screen_height))

# Durée de l'enregistrement en secondes
duration_seconds = 5

# Enregistrement de l'écran
for _ in range(int(fps * duration_seconds)):
   screenshot = pyautogui.screenshot()
   frame = np.array(screenshot)
   frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
   video_writer.write(frame)

# Libérer la ressource de l'enregistrement vidéo
video_writer.release()

print(f"L'enregistrement de l'écran est terminé. La vidéo a été enregistrée dans {output_file}.")
