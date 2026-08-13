from django.core.management.base import BaseCommand
from simulador.models import Patrocinador

class Command(BaseCommand):
    help = 'Popula o banco de dados com patrocinadores para as equipes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Buscando contratos de patrocínio no mercado...")

        # Dicionário com os patrocinadores e o quanto pagam por corrida
        patrocinadores = [
            {'nome': 'Oracle', 'pagamento_por_corrida': 1500000.00},
            {'nome': 'Petronas', 'pagamento_por_corrida': 1400000.00},
            {'nome': 'Santander', 'pagamento_por_corrida': 1200000.00},
            {'nome': 'AWS', 'pagamento_por_corrida': 1000000.00},
            {'nome': 'Pirelli', 'pagamento_por_corrida': 800000.00},
            {'nome': 'Rolex', 'pagamento_por_corrida': 900000.00},
            {'nome': 'BWT', 'pagamento_por_corrida': 700000.00},
            {'nome': 'Crypto.com', 'pagamento_por_corrida': 1100000.00},
        ]

        for dados in patrocinadores:
            patroc, criado = Patrocinador.objects.update_or_create(
                nome=dados['nome'],
                defaults={
                    'pagamento_por_corrida': dados['pagamento_por_corrida']
                }
            )
            
            if criado:
                self.stdout.write(self.style.SUCCESS(f"Novo Contrato Disponível: {patroc.nome}"))
            else:
                self.stdout.write(self.style.WARNING(f"Contrato Atualizado: {patroc.nome}"))

        self.stdout.write(self.style.SUCCESS("Todos os patrocinadores foram adicionados ao banco de dados!"))