from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.painel_geral, name='painel_geral'),
    path('garagem/', views.garagem, name='garagem'),
    path('mercado-pilotos/', views.mercado_pilotos, name='mercado_pilotos'),
    path('corrida/<int:id_pista>/', views.simular_corrida, name='simular_corrida'),
]