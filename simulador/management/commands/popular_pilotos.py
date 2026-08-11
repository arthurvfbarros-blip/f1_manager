import requests
from django.core.management.base import BaseCommand
from simulador.models import Piloto

class Command(BaseCommand):
    help = 'Puxa o histórico completo de pilotos da API Jolpica e salva no banco de dados'

    def handle(self, *args, **kwargs):
        self.stdout.write("Conectando à API do Jolpica para buscar o histórico de pilotos...")
        
        offset = 0
        limite_por_pagina = 100
        total_processado = 0
        
        while True:
            # URL atualizada: sem o "current" e com os parâmetros de paginação (limit e offset)
            url = f"https://api.jolpi.ca/ergast/f1/drivers.json?limit={limite_por_pagina}&offset={offset}"
            resposta = requests.get(url)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                lista_pilotos = dados['MRData']['DriverTable']['Drivers']
                
                # Se a lista vier vazia, chegamos ao fim do banco de dados deles
                if len(lista_pilotos) == 0:
                    break
                    
                for p in lista_pilotos:
                    nome = p['givenName']
                    sobrenome = p['familyName']
                    
                    # Mantendo as redes de segurança com o .get()
                    numero = p.get('permanentNumber', 'S/N')
                    nacionalidade = p.get('nationality', 'Desconhecida')
                    
                    piloto, criado = Piloto.objects.update_or_create(
                        nome=nome, 
                        sobrenome=sobrenome,
                        defaults={
                            'numero': numero,
                            'nacionalidade': nacionalidade
                        }
                    )
                    
                    if criado:
                        self.stdout.write(self.style.SUCCESS(f"Adicionado: {nome} {sobrenome}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Atualizado: {nome} {sobrenome}"))
                        
                # Atualizando contadores para a próxima volta do laço
                total_processado += len(lista_pilotos)
                offset += limite_por_pagina
                
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao acessar API na página {offset}: {resposta.status_code}"))
                break # Para o laço em caso de erro no servidor
                
        self.stdout.write(self.style.SUCCESS(f"Operação concluída com sucesso! {total_processado} pilotos processados no total."))