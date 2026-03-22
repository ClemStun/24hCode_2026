from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('market/', views.market, name='market'),
    path('start-screen/', views.start_screen, name='start-screen'),
    path('map/', views.map, name='map'),
    path('api/keybinds/', views.keybinds, name='keybinds'),
    path('api/tiles/import/', views.import_tiles, name='import-tiles'),
    path('api/move/', views.move, name='move'),
    path('api/get_route_to_position/', views.get_route_to_position, name='get_route_to_position'),
    path('api/get_nearest_known_island/', views.get_nearest_known_island, name='get_nearest_known_island'),
    path('api/get_not_discover_tile_in_range/', views.get_not_discover_tile_in_range, name='get_not_discover_tile_in_range'),
]
