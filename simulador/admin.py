from django.contrib import admin
from .models import FornecedorMotor, Patrocinador, Equipe, Piloto, Pista, Carro

# Registrando as tabelas para que elas apareçam na interface do administrador
admin.site.register(FornecedorMotor)
admin.site.register(Patrocinador)
admin.site.register(Equipe)
admin.site.register(Piloto)
admin.site.register(Pista)
admin.site.register(Carro)
