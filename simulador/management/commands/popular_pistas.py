import requests
from django.core.management.base import BaseCommand
from simulador.models import Pista

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write("Conectando à API do Jolpica para buscar pistas...")
        
        offset = 0
        limite_por_pagina = 100
        total_processado = 0
        
        while True:
            url = f"https://api.jolpi.ca/ergast/f1/circuits.json?limit={limite_por_pagina}&offset={offset}"
            resposta = requests.get(url)

            if resposta.status_code == 200:
                dados = resposta.json()
                lista_pistas = dados["MRData"]["CircuitTable"]["Circuits"]
                
                if len(lista_pistas) == 0:
                    break

                for p in lista_pistas:
                    nome = p['circuitName']
                    pais = p['Location']['country']
                
                    tamanho = 5.0 
                    quantidade_voltas = 50 

                    pista, criado = Pista.objects.update_or_create(
                        nome=nome,
                        defaults={
                            'pais': pais,
                            'tamanho': tamanho,
                            'quantidade_voltas': quantidade_voltas,
                        }
                    )

                    if criado:
                        self.stdout.write(self.style.SUCCESS(f"Adicionada: {nome} ({pais})"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Atualizada: {nome} ({pais})"))
                
                total_processado += len(lista_pistas)
                
                offset += limite_por_pagina
                        
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao acessar API na página {offset}: {resposta.status_code}"))
                break
                
        self.stdout.write(self.style.SUCCESS(f"Operação concluída! {total_processado} pistas processadas no total."))