from django.urls import path
from . import views

urlpatterns = [
    path('', views.painel_geral, name='home'),
    path('painel/', views.painel_geral, name='painel_geral'),
    path('garagem/', views.garagem, name='garagem'),
    path('mercado-pilotos/', views.mercado_pilotos, name='mercado_pilotos'),
    path('contratar-piloto/<int:piloto_id>/', views.contratar_piloto, name='contratar_piloto'),
    path('corrida/<int:id_pista>/', views.simular_corrida, name='simular_corrida'),
    path('avancar-tempo/', views.avancar_tempo, name='avancar_tempo'),
    path('novo-jogo/', views.novo_jogo, name='novo_jogo'),
    path('setup-equipe/', views.setup_equipe, name='setup_equipe'),
    path('fim-de-semana/<int:id_pista>/', views.fim_de_semana_hub, name='fim_de_semana_hub'),
    path('sessao/<int:id_pista>/<str:tipo_sessao>/', views.sessao_simulacao, name='sessao_simulacao'),
    path('campeonato/', views.campeonato, name='campeonato'),
]