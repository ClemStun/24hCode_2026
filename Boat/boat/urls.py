from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start-screen/', views.start_screen, name='start-screen'),
    path('map/', views.map, name='map'),
    path('api/keybinds/', views.keybinds, name='keybinds'),
]
