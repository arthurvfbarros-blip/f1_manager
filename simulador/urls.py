from django.urls import path
from . import views

urlpatterns = [
    path('', views.painel_geral, name='home'),
    path('painel/', views.painel_geral, name='painel_geral'),
    path('garagem/', views.garagem, name='garagem'),
    path('mercado-pilotos/', views.mercado_pilotos, name='mercado_pilotos'),
    path('corrida/<int:id_pista>/', views.simular_corrida, name='simular_corrida'),
    path('avancar-tempo/', views.avancar_tempo, name='avancar_tempo'),
    path('novo-jogo/', views.novo_jogo, name='novo_jogo'),
]