from itertools import groupby
import json
from operator import attrgetter

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from .models import Case, CurrentState, Keybind

# Create your views here.
def index(request):
    return redirect('start-screen')

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
                zone=tile['zone']
            )
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