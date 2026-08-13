import requests
from django.core.management.base import BaseCommand
from simulador.models import Equipe, Carro

class Command(BaseCommand):
    help = 'Puxa o histórico de construtores da API e cria as equipes e seus carros'

    def handle(self, *args, **kwargs):
        self.stdout.write("Conectando à API do Jolpica para buscar as equipes...")
        
        offset = 0
        limite_por_pagina = 100
        total_processado = 0
        
        while True:
            # Endpoint específico para os construtores
            url = f"https://api.jolpi.ca/ergast/f1/constructors.json?limit={limite_por_pagina}&offset={offset}"
            resposta = requests.get(url)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                lista_equipes = dados['MRData']['ConstructorTable']['Constructors']
                
                # Se a lista vier vazia, acabou a base de dados
                if len(lista_equipes) == 0:
                    break
                    
                for eq in lista_equipes:
                    nome_equipe = eq['name']
                    
                    # 1. Cria a equipe no banco (dando 100 Milhões iniciais para todas)
                    nova_equipe, equipe_criada = Equipe.objects.update_or_create(
                        nome=nome_equipe,
                        defaults={
                            'orcamento': 100000000.00
                        }
                    )
                    
                    # 2. Cria a carcaça do carro (Chassi e Aero) atrelada a essa equipe!
                    # Usamos get_or_create para não duplicar o carro se rodarmos o script duas vezes
                    Carro.objects.get_or_create(equipe=nova_equipe)
                    
                    if equipe_criada:
                        self.stdout.write(self.style.SUCCESS(f"Adicionada: {nome_equipe} (Carro construído!)"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Atualizada: {nome_equipe}"))
                        
                total_processado += len(lista_equipes)
                offset += limite_por_pagina
                
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao acessar API na página {offset}: {resposta.status_code}"))
                break 
                
        self.stdout.write(self.style.SUCCESS(f"Operação concluída! {total_processado} equipes prontas para correr."))