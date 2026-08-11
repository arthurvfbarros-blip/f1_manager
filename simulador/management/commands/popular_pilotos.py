import requests
from django.core.management.base import BaseCommand
from simulador.models import Piloto

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        url = "https://api.jolpi.ca/ergast/f1/drivers.json?limit=1000"
        self.stdout.write("Conectando à API do jolpica...")

        resposta = requests.get(url)

        if resposta.status_code == 200:
            dados = resposta.json()
            lista_pilotos = dados["MRData"]["DriverTable"]["Drivers"]

            for p in lista_pilotos:
                nome = p['givenName']
                sobrenome = p['familyName']
                numero = p.get('permanentNumber', 'S/N')
                nacionalidade = p.get('nationality', 'Desconhecida')

                piloto, criado = Piloto.objects.update_or_create(
                    nome = nome,
                    sobrenome = sobrenome,
                    defaults={
                        'numero': numero,
                        'nacionalidade': nacionalidade,
                    }
                )

                if criado:
                    self.stdout.write(self.style.SUCCESS(f"Adicionado: {nome} {sobrenome}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Atualizado: {nome} {sobrenome}"))
                    
            self.stdout.write(self.style.SUCCESS(f"Operação concluída! {len(lista_pilotos)} pilotos processados."))
        else:
            self.stdout.write(self.style.ERROR(f"Erro ao acessar API: {resposta.status_code}"))