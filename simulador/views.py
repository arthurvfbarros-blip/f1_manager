from django.shortcuts import render
from .models import Equipe, Piloto, Pista

def painel_geral(request):
    minha_equipe = Equipe.objects.get(id=1)

    contexto = {
        'equipe': minha_equipe,
        'saldo': minha_equipe.orcamento
    }
    return render(request, 'simulador/painel.html', contexto)

def garagem(request):
    minha_equipe = Equipe.objects.get(id=1)
    return render(request, 'simulador/garagem.html', {'equipe': minha_equipe})
