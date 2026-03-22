import pygame
import json
import requests
import os
import sys
import heapq

API_URL = "http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
HEADERS = {"codinggame-id": TOKEN}
MAP_FILE = "map_discovered.json"
CELL_SIZE = 24
MIN_CELL_SIZE = 2
MAX_CELL_SIZE = 80
WIDTH, HEIGHT = 1300, 900
DIRECTIONS_MAP = {pygame.K_UP: "NE", pygame.K_DOWN: "S", pygame.K_LEFT: "W", pygame.K_RIGHT: "E"}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Map Interactive 3026 (Pygame)")
font = pygame.font.SysFont("Arial", 18)

def charger_iles_depuis_json(chemin_fichier):
    """Lit un fichier JSON et retourne une liste de tuples (x, y) pour les îles."""
    iles_trouvees = []
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
            donnees = json.load(fichier)

        carte = donnees.get("map", {})
        for cle, details_case in carte.items():
            if "island" in details_case:
                iles_trouvees.append((details_case["x"], details_case["y"]))

    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")

    return iles_trouvees

def calculer_distance_manhattan(p1, p2):
    distance_x = abs(p1[0] - p2[0])
    distance_y = abs(p1[1] - p2[1])
    return distance_x + distance_y

def trouver_itineraire_navire(depart, arrivee, iles, deplacement_max):
    tous_les_points = [depart, arrivee] + iles
    graphe = {point: [] for point in tous_les_points}

    # Création du réseau avec la nouvelle distance de Manhattan
    for i in range(len(tous_les_points)):
        for j in range(i + 1, len(tous_les_points)):
            point_a = tous_les_points[i]
            point_b = tous_les_points[j]
            dist = calculer_distance_manhattan(point_a, point_b)

            if dist <= deplacement_max:
                graphe[point_a].append((dist, point_b))
                graphe[point_b].append((dist, point_a))

    # Algorithme de Dijkstra (inchangé, il fonctionne parfaitement avec la nouvelle distance)
    a_explorer = [(0, depart)]
    distances = {point: float('infinity') for point in tous_les_points}
    distances[depart] = 0
    provenance = {point: None for point in tous_les_points}

    while a_explorer:
        dist_actuelle, point_actuel = heapq.heappop(a_explorer)

        if point_actuel == arrivee:
            break

        if dist_actuelle > distances[point_actuel]:
            continue

        for cout_voyage, voisin in graphe[point_actuel]:
            distance_totale = dist_actuelle + cout_voyage

            if distance_totale < distances[voisin]:
                distances[voisin] = distance_totale
                provenance[voisin] = point_actuel
                heapq.heappush(a_explorer, (distance_totale, voisin))

    if distances[arrivee] == float('infinity'):
        return None

    # Reconstruction du chemin
    chemin = []
    point_en_cours = arrivee
    while point_en_cours is not None:
        chemin.append(point_en_cours)
        point_en_cours = provenance[point_en_cours]

    chemin.reverse()
    return chemin

def get_player_pos():
        return (-30, 4)

def get_map():
    if not os.path.exists(MAP_FILE):
        return {}
    with open(MAP_FILE, "r") as f:
        data = json.load(f)
    return data.get("map", {})

def move_ship(direction):
    r = requests.post(f"{API_URL}/ship/move", headers=HEADERS, json={"direction": direction})
    if r.status_code == 200:
        return r.json()
    return None

def show_player_info():
    try:
        r = requests.get(f"{API_URL}/players/details", headers=HEADERS)
        r.raise_for_status()
        info = r.json()
        msg = f"Nom: {info['name']} | Energie: {info['ship']['availableMove']} | Argent: {info['money']} | Îles découvertes: {len(info.get('discoveredIslands', []))}"
        print(msg)
        return msg
    except Exception as e:
        print("Erreur infos joueur:", e)
        return str(e)

def draw_map(player_pos, energy=None):
    global CELL_SIZE
    screen.fill((255, 255, 255))
    cells = get_map()
    px, py = player_pos
    for key, cell in cells.items():
        try:
            x, y = map(int, key.split(","))
            # Décale chaque case par rapport à la position du bateau
            rel_x = x - px
            rel_y = y - py
            cell_type = cell.get("type", "SEA")
            if cell_type == "SEA":
                if cell["zone"] == 1:
                    color = (51, 153, 255)
                elif cell["zone"] == 2:
                    color = (0, 102, 204)
                elif cell["zone"] == 3:
                    color = (0, 51, 153)
                elif cell["zone"] == 4:
                    color = (0, 25, 102)
                else:
                    color = (51, 153, 255)
            elif cell_type in ("SAND", "ISLAND"):
                if cell["zone"] == 1:
                    color = (255, 215, 0)
                elif cell["zone"] == 2:
                    color = (255, 200, 0)
                elif cell["zone"] == 3:
                    color = (255, 185, 0)
                elif cell["zone"] == 4:
                    color = (255, 170, 0)
                else:
                    color = (255, 215, 0)
            else:
                color = (120, 120, 120)
            cx = WIDTH // 2 + rel_x * CELL_SIZE
            cy = HEIGHT // 2 + rel_y * CELL_SIZE  # Inversion de l'axe Y
            pygame.draw.rect(screen, color, (cx-10*CELL_SIZE//24, cy-10*CELL_SIZE//24, 20*CELL_SIZE//24, 20*CELL_SIZE//24))
        except Exception:
            continue
    # Draw player (toujours au centre)
    cx = WIDTH // 2
    cy = HEIGHT // 2
    pygame.draw.rect(screen, (255, 0, 0), (cx-12*CELL_SIZE//24, cy-12*CELL_SIZE//24, 24*CELL_SIZE//24, 24*CELL_SIZE//24), 3)
    text = font.render(f"Position bateau: {player_pos}", True, (0, 0, 0))
    screen.blit(text, (20, 20))
    if energy is not None:
        energy_text = font.render(f"Energie: {energy}", True, (0, 0, 0))
        screen.blit(energy_text, (20, 40))
    pygame.display.flip()

def save_cell(cell):
    try:
        with open("map_discovered.json", "r") as f:
            data = json.load(f)

        if data["map"] is None:
            data["map"] = {}
    except Exception as e:
        print("Erreur lors de la lecture de map_discovered.json :", e)
        data = {"map": {}}
    cell_key = f"{cell['x']},{cell['y']}"
    if cell_key not in data["map"]:
        data["map"][cell_key] = cell
        with open("map_discovered.json", "w") as f:
            json.dump(data, f, indent=2)

def main():
    global CELL_SIZE
    player_pos = list(get_player_pos())
    info_msg = ""
    running = True
    energy = None
    draw_map(player_pos)
    auto_move = False
    target_coords = None

    def go_to_target(start_pos, target):
        nonlocal player_pos, energy, running
        x, y = start_pos
        tx, ty = target
        while running and (x != tx or y != ty):
            if x < tx:
                direction = "E"
            elif x > tx:
                direction = "W"
            elif y < ty:
                direction = "S"
            elif y > ty:
                direction = "N"
            else:
                break
            resp = move_ship(direction)
            if resp and "position" in resp:
                x = resp["position"]["x"]
                y = resp["position"]["y"]
                player_pos[0] = x
                player_pos[1] = y
                energy = resp["energy"]
                draw_map(player_pos, energy)
                for cell in resp["discoveredCells"]:
                    save_cell(cell)
                pygame.time.wait(1000)  # Petite pause pour voir le déplacement
            else:
                print("Déplacement impossible ou bloqué")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in DIRECTIONS_MAP:
                    resp = move_ship(DIRECTIONS_MAP[event.key])
                    if resp and "position" in resp:
                        player_pos[0] = resp["position"]["x"]
                        player_pos[1] = resp["position"]["y"]
                        energy = resp["energy"]
                        draw_map(player_pos, energy)
                        for cell in resp["discoveredCells"]:
                            save_cell(cell)
                    else:
                        print("Déplacement impossible")
                elif event.key == pygame.K_i:
                    info_msg = show_player_info()
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    if CELL_SIZE < MAX_CELL_SIZE:
                        CELL_SIZE += 4
                        draw_map(player_pos, energy)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    if CELL_SIZE > MIN_CELL_SIZE:
                        CELL_SIZE -= 4
                        draw_map(player_pos, energy)
                elif event.key == pygame.K_g:
                    # Saisie des coordonnées cibles
                    try:
                        x_str = input("Coordonnée X cible : ")
                        y_str = input("Coordonnée Y cible : ")
                        tx = int(x_str)
                        ty = int(y_str)
                        print(f"Déplacement automatique vers ({tx}, {ty})...")
                        iles = charger_iles_depuis_json("map_discovered.json")
                        itineraire_complet = trouver_itineraire_navire(tuple(player_pos), (tx, ty), iles, energy)
                        for point in itineraire_complet[1:]:
                            go_to_target(tuple(player_pos), point)  # Ignorer la position actuelle
                    except Exception as e:
                        print("Entrée invalide :", e)
        draw_map(player_pos, energy)
        # Affiche l'info joueur en bas si demandée
        if info_msg:
            pygame.draw.rect(screen, (255,255,255), (0, HEIGHT-40, WIDTH, 40))
            info_text = font.render(info_msg, True, (0,0,0))
            screen.blit(info_text, (20, HEIGHT-30))
            pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
