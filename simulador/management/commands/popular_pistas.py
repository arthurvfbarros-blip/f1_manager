import requests
from django.core.management.base import BaseCommand
from simulador.models import Pista

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        url = "https://api.jolpi.ca/ergast/f1/circuits.json?limit=1000"
        self.stdout.write("Conectando à API do jolpica...")

        resposta = requests.get(url)

        if resposta.status_code == 200:
            dados = resposta.json()
            lista_pistas = dados["MRData"]["DriverTable"]["Drivers"]

            for p in lista_pistas:
                nome = p['circuitName']
                pais = p['Location']
                tamanho = p.get('permanentNumber', 'S/N')
                quantidade_voltas = p.get('nationality', 'Desconhecida')

                pista, criado = Pista.objects.update_or_create(
                    nome = nome,
                    pais = pais,
                    defaults={
                        'tamanho': tamanho,
                        'quantidade_voltas': quantidade_voltas,
                    }
                )

                if criado:
                    self.stdout.write(self.style.SUCCESS(f"Adicionado: {nome} {pais}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Atualizado: {nome} {pais}"))
                    
            self.stdout.write(self.style.SUCCESS(f"Operação concluída! {len(lista_pilotos)} pilotos processados."))
        else:
            self.stdout.write(self.style.ERROR(f"Erro ao acessar API: {resposta.status_code}"))