import random
from django.core.management.base import BaseCommand
from simulador.models import Equipe, Piloto

class Command(BaseCommand):
    help = 'Distribui aleatoriamente 2 pilotos para cada equipe no banco de dados'

    def handle(self, *args, **kwargs):
        # Puxa todas as equipes e pilotos e os transforma em listas Python clássicas
        equipes = list(Equipe.objects.all())
        pilotos = list(Piloto.objects.all())

        # Trava de segurança
        if not equipes or not pilotos:
            self.stdout.write(self.style.ERROR("Você precisa ter equipes e pilotos no banco primeiro!"))
            return

        if len(pilotos) < len(equipes) * 2:
            self.stdout.write(self.style.ERROR("Você não tem pilotos suficientes para preencher 2 vagas por equipe!"))
            return

        self.stdout.write("A janela de transferências está aberta! Sorteando contratos...")

        # A mágica acontece aqui: embaralhamos a lista de pilotos!
        random.shuffle(pilotos)

        pilotos_contratados = 0

        # Para cada equipe, pegamos os próximos 2 pilotos da lista embaralhada
        for equipe in equipes:
            piloto_1 = pilotos[pilotos_contratados]
            piloto_2 = pilotos[pilotos_contratados + 1]

            # Assinando o contrato (vinculando a equipe ao piloto)
            piloto_1.equipe_atual = equipe
            piloto_2.equipe_atual = equipe

            # Salvando no banco de dados
            piloto_1.save()
            piloto_2.save()

            pilotos_contratados += 2
            
            self.stdout.write(self.style.SUCCESS(f"[{equipe.nome}] contratou: {piloto_1.nome} {piloto_1.sobrenome} e {piloto_2.nome} {piloto_2.sobrenome}"))

        sobra = len(pilotos) - pilotos_contratados
        self.stdout.write(self.style.SUCCESS(f"Operação concluída! {pilotos_contratados} pilotos empregados. {sobra} pilotos continuam como Agentes Livres no mercado."))