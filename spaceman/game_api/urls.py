from django.urls import include, path

from game_api.views import *

urlpatterns = [
    path('game/', game_view ),
    path('game/<str:game_id>/', game_view ),
    path('game/<str:game_id>/solution/', game_solution )
]