from django.core.management.base import BaseCommand
from simulador.models import FornecedorMotor

class Command(BaseCommand):
    help = 'Popula o banco de dados com os principais fornecedores de motor da F1'

    def handle(self, *args, **kwargs):
        self.stdout.write("Injetando fornecedores de motor na oficina...")

        # Dicionário com os atributos balanceados para o jogo
        # Potência e Confiabilidade vão de 1 a 100.
        motores = [
            {'nome': 'Mercedes', 'potencia': 95, 'confiabilidade': 90, 'preco': 15000000.00},
            {'nome': 'Ferrari', 'potencia': 98, 'confiabilidade': 82, 'preco': 14500000.00},
            {'nome': 'Honda (RBPT)', 'potencia': 96, 'confiabilidade': 88, 'preco': 14000000.00},
            {'nome': 'Renault', 'potencia': 85, 'confiabilidade': 80, 'preco': 10000000.00},
            {'nome': 'Cosworth (Clássico)', 'potencia': 80, 'confiabilidade': 95, 'preco': 8000000.00},
            {'nome': 'Audi', 'potencia': 88, 'confiabilidade': 75, 'preco': 12000000.00},
            {'nome': 'Judd (Barato)', 'potencia': 70, 'confiabilidade': 60, 'preco': 4000000.00},
        ]

        for dados in motores:
            motor, criado = FornecedorMotor.objects.update_or_create(
                nome=dados['nome'],
                defaults={
                    'potencia': dados['potencia'],
                    'confiabilidade': dados['confiabilidade'],
                    'preco': dados['preco']
                }
            )
            
            if criado:
                self.stdout.write(self.style.SUCCESS(f"Motor Fabricado: {motor.nome}"))
            else:
                self.stdout.write(self.style.WARNING(f"Motor Atualizado: {motor.nome}"))

        self.stdout.write(self.style.SUCCESS("Todos os motores foram entregues às equipes!"))