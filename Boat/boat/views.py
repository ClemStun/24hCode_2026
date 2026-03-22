import json
import requests
import random
from itertools import groupby
from operator import attrgetter
from .utils.graph import trouver_itineraire_navire

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from .models import Case, CurrentState, Keybind

# Create your views here.
def index(request):
    return redirect('start-screen')

def market(request):
    resp = requests.get(
        'http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/marketplace/offers',
        headers={
            "codinggame-id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
        }
    )
    offers = resp.json()
    return render(request, 'market.html', {'offers': offers})


def start_screen(request):
    return render(request, 'start-screen.html')

def map(request):
    state = CurrentState.objects.first() or CurrentState.objects.create()
    tiles = Case.objects.all()
    tiles_list = [
        {
            'id': str(tile.id),
            'x': tile.x,
            'y': tile.y,
            'type': tile.type,
            'zone': tile.zone,
        }
        for tile in tiles
    ]

    data = {
        'tiles': tiles_list,
        'currentPosition': {
            'x': state.position_x,
            'y': state.position_y,
            'direction': state.direction
        },
        'resources': {
            'boisium': state.boisium,
            'feronium': state.feronium,
            'charbonium': state.charbonium,
            'gold': state.gold,
        },
        'boat': {
            'level': state.boat_level,
            'remainingMovement': state.remaining_movement,
            'maxMovement': state.max_movement,
        }
    }

    return render(request, 'map.html', {'data': data})

def keybinds(request):
    if request.method == 'GET':
        return get_keybinds(request)
    elif request.method == 'POST' or request.method == 'PUT':
        return update_keybinds(request)
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'PUT'])

def get_keybinds(request):
    keybinds = Keybind.objects.all().order_by('action')
    keybinds_dict = {
        action: [kb.key for kb in group]
        for action, group in groupby(keybinds, key=attrgetter('action'))
    }
    return JsonResponse(keybinds_dict)

def update_keybinds(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # data doit être un dict {action: [keys]}
    if not isinstance(data, dict):
        return JsonResponse({'status': 'error', 'message': 'Invalid data format'}, status=400)

    # On supprime tous les keybinds existants
    Keybind.objects.all().delete()

    # On recrée les keybinds à partir du JSON
    for action, keys in data.items():
        if not isinstance(keys, list):
            continue
        for key in keys:
            Keybind.objects.create(action=action, key=key)

    # Réponse No Content (204) sans body
    return HttpResponse(status=204)

def import_tiles(request):
    if request.method == 'POST':
        data = get_tiles_data(request)
        if isinstance(data, dict) and 'map' in data:
            data = data['map']

        if isinstance(data, dict):
            data = data.values()

        for tile in data:
            Case.objects.update_or_create(
                id=tile['id'],
                x=tile['x'],
                y=tile['y'],
                type=tile['type'],
                name=tile.get('island', {}).get('name', ''),
                state=tile.get('state', 'KNOWN'),
                zone=tile['zone']
            )

        return JsonResponse({'status': 'success'})
    else:
        return HttpResponseNotAllowed(['POST'])

def get_tiles_data(request):
    try:
        return json.loads(request.body)
    except Exception:
        try:
            return json.load(request.FILES['file'])
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON or file'}, status=400)

def move(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            direction = data.get('direction')
            if direction not in ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']:
                return JsonResponse({'status': 'error', 'message': 'Invalid direction'}, status=400)
            res = requests.post(
                'http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/ship/move',
                headers={
                    "codinggame-id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
                },
                json={"direction": direction}
            )

            if res.status_code != 200:
                return JsonResponse({'status': 'error', 'message': f'API error: {res.status_code}'}, status=500)

            res_data = res.json()
            state = CurrentState.objects.first() or CurrentState.objects.create()
            state.position_x = res_data['position']['x']
            state.position_y = res_data['position']['y']
            state.direction = direction
            state.remaining_movement = res_data['energy']

            state.save()

            return JsonResponse({'status': 'success', 'data': {
                'position': {
                    'x': state.position_x,
                    'y': state.position_y,
                },
                'direction': state.direction,
                'remaining_movement': state.remaining_movement,
            }})
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return HttpResponseNotAllowed(['POST'])

def get_not_discover_tile_in_range(request):
    if request.method == 'GET':
        try:
            state = CurrentState.objects.first()
            x = state.position_x
            y = state.position_y
            max_distance = int(request.GET.get('distance', 15))

            not_discover_tiles = []
            for x_pos in range(x - max_distance, x + max_distance + 1):
                for y_pos in range(y - max_distance, y + max_distance + 1):
                    if max(abs(x_pos - x), abs(y_pos - y)) == max_distance and not Case.objects.filter(x=x_pos, y=y_pos).first():
                        not_discover_tiles.append({'x': x_pos, 'y': y_pos})

            return JsonResponse({'status': 'success', 'tiles': random.choice(not_discover_tiles) if not_discover_tiles else None})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET'])

def get_nearest_known_island(request):
    if request.method == 'GET':
        try:
            state = CurrentState.objects.first()
            x = state.position_x
            y = state.position_y

            known_islands = Case.objects.filter(type="SAND", state="KNOWN")
            nearest_island = min(known_islands, key=lambda island: max(abs(island.x - x), abs(island.y - y)), default=None)

            if nearest_island:
                return JsonResponse({'status': 'success', 'island': {'x': nearest_island.x, 'y': nearest_island.y}})
            else:
                return JsonResponse({'status': 'success', 'island': None})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET'])

def get_route_to_position(request):
    if request.method == 'GET':
        try:
            state = CurrentState.objects.first()
            tx = int(request.GET.get('target_x'))
            ty = int(request.GET.get('target_y'))
            route = trouver_itineraire_navire((state.position_x, state.position_y), (tx, ty), state.max_movement)
            # Ici, vous pouvez ajouter la logique pour calculer la route vers la position cible
            return JsonResponse({'status': 'success', 'route': route})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid parameters'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET'])