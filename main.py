import cv2
import cv2.aruco as aruco
from pyallegro5 import allegro, display, primitives, font

# Initialisation d'Allegro
allegro.al_install_system(allegro.ALLEGRO_VERSION_INT, None)

# Initialisation d'Allegro Display
allegro.al_set_new_display_flags(allegro.ALLEGRO_WINDOWED)
display = allegro.al_create_display(800, 600)

# Initialisation de la police pour l'affichage du nombre de places
font.init()
font_18 = font.load_builtin_font()

# Charger le dictionnaire ArUco
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

# Charger les paramètres de la caméra (à ajuster selon votre caméra)
camera_matrix = [...]  # Matrice de la caméra
dist_coeffs = [...]    # Coefficients de distorsion

# Initialiser le détecteur ArUco
parameters = aruco.DetectorParameters_create()

# Charger l'image depuis la caméra
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détecter les marqueurs ArUco
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # Dessiner les contours autour des marqueurs détectés
    if ids is not None:
        aruco.drawDetectedMarkers(frame, corners, ids)

        # Compter le nombre de sièges
        nombre_de_places = len(ids)

        # Afficher le nombre de places disponibles à l'aide d'Allegro
        allegro.al_clear_to_color(allegro.al_map_rgb(0, 0, 0))  # Fond noir
        allegro.al_draw_text(font_18, allegro.al_map_rgb(255, 255, 255), 10, 10, 0, f'Places disponibles : {nombre_de_places}')

        # Afficher le contenu d'Allegro Display
        allegro.al_flip_display()

    # Sortir de la boucle si la touche 'q' est pressée
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources Allegro
allegro.al_uninstall_system()

# Libérer les ressources OpenCV
cap.release()
cv2.destroyAllWindows()
