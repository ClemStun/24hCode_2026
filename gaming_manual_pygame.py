import pygame
import json
import requests
import os
import sys
import heapq
import random

API_URL = "http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
HEADERS = {"codinggame-id": TOKEN}
MAP_FILE = "map_discovered.json"
map_game = {}
CELL_SIZE = 24
MIN_CELL_SIZE = 2
MAX_CELL_SIZE = 80
WIDTH, HEIGHT = 1300, 900
player_pos = [-84, -38]
energy = 200


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Map Interactive 3026 (Pygame)")
font = pygame.font.SysFont("Arial", 18)

def get_nearest_unexplored_tile(player_pos, max_distance=100):
    min_distance = float('inf')
    nearest_tiles = []
    for tile in map_game.values():
        if tile["type"] == "SAND":
            for dx in range(-max_distance, max_distance + 1):
                for dy in range(-max_distance, max_distance + 1):
                    pos_tile = (tile["x"] + dx, tile["y"] + dy)
                    check_key = f"{pos_tile[0]},{pos_tile[1]}"
                    if check_key not in map_game:
                        distance = calculer_distance(player_pos, pos_tile)
                        if distance < min_distance and calculer_distance_manhattan(pos_tile, (0, 0)) > 145:
                            min_distance = distance
                            nearest_tiles.append(pos_tile)
    print(f"Tuile non explorée la plus proche : {nearest_tiles} à une distance de {min_distance}")
    return max(nearest_tiles, key=lambda pos: calculer_distance((0, 0), pos)) if nearest_tiles else None

def get_known_islands():
    response = requests.get(f"{API_URL}/players/details", headers=HEADERS)
    res_json = response.json()
    islands = [island["island"] for island in res_json["discoveredIslands"] if island["islandState"] == "KNOWN"]
    return islands

def get_known_islands_names():
    islands = get_known_islands()
    return [island["name"] for island in islands]

def get_islands_tiles_positions_from_names(island_names):
    return [(island["x"], island["y"]) for island in map_game.values() if island["type"] == "SAND" and island["island"]["name"] in island_names]

def get_nearest_known_island(player_pos):
    known_islands_name = get_known_islands_names()
    known_island_pos = get_islands_tiles_positions_from_names(known_islands_name)
    nearest_island = min(known_island_pos, key=lambda pos: calculer_distance(player_pos, pos))
    return nearest_island

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

def calculer_distance(p1, p2):
    """Calcule la distance de Tchebychev (inclut les diagonales à coût 1)."""
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def generer_virages(points):
    """
    Avec les diagonales, le trajet direct est le plus court.
    On retourne simplement la liste des points clés.
    """
    return points

def trouver_itineraire_navire(depart, arrivee, deplacement_max):
    """
    Trouve un chemin utilisant uniquement les îles connues, 
    puis vérifie si l'aller-retour vers l'objectif est possible.
    """
    # 1. Identifier les "Portails" (îles connues assez proches de l'arrivée pour l'A/R)
    portails_possibles = []
    iles_connues = get_islands_tiles_positions_from_names(get_known_islands_names())
    for ile in iles_connues:
        dist_ar = calculer_distance(ile, arrivee)
        if dist_ar * 2 <= deplacement_max:
            portails_possibles.append(ile)

    # Si le départ lui-même permet l'aller-retour
    if calculer_distance(depart, arrivee) * 2 <= deplacement_max:
        portails_possibles.append(depart)

    if not portails_possibles:
        print("/!\\ Impossible : Aucune île connue n'est assez proche pour l'aller-retour.")
        plus_proche = min(iles_connues, key=lambda x: calculer_distance(x, arrivee))
        return None, plus_proche

    # 2. Dijkstra pour aller du départ vers l'un des portails
    tous_points = list(set([depart] + iles_connues))
    graphe = {p: [] for p in tous_points}
    for i in range(len(tous_points)):
        for j in range(i + 1, len(tous_points)):
            p1, p2 = tous_points[i], tous_points[j]
            d = calculer_distance(p1, p2)
            if d <= deplacement_max:
                graphe[p1].append((d, p2))
                graphe[p2].append((d, p1))

    a_explorer = [(0, depart)]
    distances = {p: float('inf') for p in tous_points}
    distances[depart] = 0
    provenance = {p: None for p in tous_points}

    while a_explorer:
        d_actuelle, p_actuel = heapq.heappop(a_explorer)
        if d_actuelle > distances[p_actuel]: continue
        for cout, voisin in graphe[p_actuel]:
            if d_actuelle + cout < distances[voisin]:
                distances[voisin] = d_actuelle + cout
                provenance[voisin] = p_actuel
                heapq.heappush(a_explorer, (distances[voisin], voisin))

    meilleur_portail = None
    min_dist = float('inf')
    for p in portails_possibles:
        if distances[p] < min_dist:
            min_dist = distances[p]
            meilleur_portail = p

    if meilleur_portail is None or distances[meilleur_portail] == float('inf'):
        return None, None

    # 3. Reconstruction du chemin
    chemin_cles = []
    curr = meilleur_portail
    while curr is not None:
        chemin_cles.append(curr)
        curr = provenance[curr]
    chemin_cles.reverse()

    # Itinéraire : Aller aux îles -> Objectif -> Retour sécurité à l'île
    itineraire_final_cles = chemin_cles + [arrivee]

    return itineraire_final_cles

def get_map():
    global map_game
    if not os.path.exists(MAP_FILE):
        return {}
    with open(MAP_FILE, "r") as f:
        data = json.load(f)
    map_game = data.get("map", {})

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
    px, py = player_pos
    for key, cell in map_game.items():
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
                    color = (0, 0, 0)
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

def go_to_target(start_pos, target):
        x, y = start_pos
        tx, ty = target
        while (x != tx or y != ty):
            get_map()
            direction = ""
            if y > ty:
                direction = direction + "N"
            elif y < ty:
                direction = direction + "S"
            if x > tx:
                direction = direction + "W"
            elif x < tx:
                direction = direction + "E"

            resp = move_ship(direction)
            if resp and "position" in resp:
                x = resp["position"]["x"]
                y = resp["position"]["y"]
                player_pos[0] = x
                player_pos[1] = y
                energy = resp["energy"]
                print(f"Déplacement vers {direction} - Nouvelle position: ({x}, {y}), Energie restante: {energy}")
                draw_map(player_pos, energy)
                for cell in resp["discoveredCells"]:
                    save_cell(cell)
                pygame.time.wait(800)  # Petite pause pour voir le déplacement
            else:
                print("Déplacement impossible ou bloqué")
                break

def main():
    running = True
    get_map()

    while running:
        draw_map(player_pos, energy)
        nearest_tile = get_nearest_unexplored_tile(player_pos)
        if nearest_tile:
            print("Aller vers la tuile non explorée la plus proche :", nearest_tile)
            itineraire_complet = trouver_itineraire_navire(tuple(player_pos), nearest_tile, 200)
            print("Itinéraire complet vers la tuile non explorée :", itineraire_complet)
            for point in itineraire_complet[1:]:
                go_to_target(tuple(player_pos), point)
            go_to_target(player_pos, get_nearest_known_island(player_pos))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
