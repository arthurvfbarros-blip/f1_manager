from django.core.management.base import BaseCommand
from simulador.models import Equipe, Piloto

class Command(BaseCommand):
    help = 'Reseta os contratos e define o grid atual da Fórmula 1'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpando contratos antigos...")
        
        # DEMISSÃO EM MASSA: Zera a equipe de todos os pilotos do banco
        Piloto.objects.all().update(equipe_atual=None)
        
        self.stdout.write("Assinando os contratos reais da temporada...")


        contratos_iniciais = {
            "Red Bull": ["Max", "Isack"],
            "Mercedes": ["George", "Kimi"],
            "Mclaren": ["Lando", "Oscar"],
            "Alpine": ["Pierre", "Franco"],
            "RB": ["Liam", "Arvid"],
            "Audi": ["Gabriel", "Nico"],
            "Cadillac": ["Sergio", "Valtteri"],
            "Haas": ["Oliver", "Esteban"],
            "Ferrari": ["Charles", "Lewis"],
            "Aston Martin": ["Fernando", "Lance"],
            "Williams": ["Carlos", "Alex"],
        }

        pilotos_alocados = 0


        for nome_equipe, nomes_pilotos in contratos_iniciais.items():
            # Busca a equipe no banco (tem que já ter sido criada!)
            equipe = Equipe.objects.filter(nome__icontains=nome_equipe).first()
            
            if equipe:
                for nome_piloto in nomes_pilotos:
                    # Busca o piloto usando o sobrenome/nome que contenha o texto
                    piloto = Piloto.objects.filter(sobrenome__icontains=nome_piloto).first()
                    
                    if not piloto: # Tenta pelo nome se não achar pelo sobrenome
                        piloto = Piloto.objects.filter(nome__icontains=nome_piloto).first()
                        
                    if piloto:
                        piloto.equipe_atual = equipe
                        piloto.save()
                        pilotos_alocados += 1
                        self.stdout.write(self.style.SUCCESS(f"{piloto.nome} {piloto.sobrenome} assinou com a {equipe.nome}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"Piloto {nome_piloto} não encontrado no banco!"))
            else:
                self.stdout.write(self.style.ERROR(f"Equipe {nome_equipe} não encontrada no banco!"))

        self.stdout.write(self.style.SUCCESS(f"Grid formado! {pilotos_alocados} pilotos titulares definidos."))