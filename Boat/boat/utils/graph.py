import heapq
import requests
from ..models import Case

def get_known_islands():
    response = requests.get(
        'http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/players/details',
        headers={
            "codinggame-id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
        }
    )
    res_json = response.json()
    islands = [island["island"] for island in res_json["discoveredIslands"] if island["islandState"] == "KNOWN"]
    return islands

def get_known_islands_names():
    islands = get_known_islands()
    return [island["name"] for island in islands]

def get_islands_tiles_positions_from_names(island_names):
    cases = Case.objects.filter(type="SAND", name__in=island_names)
    return [(island.x, island.y) for island in cases]

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