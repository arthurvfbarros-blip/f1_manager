from django.core.management.base import BaseCommand
from simulador.models import Temporada, EtapaCalendario, Pista

class Command(BaseCommand):
    help = 'Cria a Temporada 2026 e o calendário de 24 corridas na ordem oficial'

    def handle(self, *args, **kwargs):
        self.stdout.write("Montando o calendário da temporada...")

        # 1. Cria a Temporada (Se já existir, ele só pega ela)
        temporada_2024, criada = Temporada.objects.get_or_create(ano=2024, defaults={'etapa_atual': 1})
        
        # Lista com a ordem real do calendário da F1
        calendario_oficial = [
            "Austrália", "Bahrein", "Arábia Saudita", "Japão", "China", 
            "Miami", "Emília-Romanha", "Mônaco", "Canadá", "Espanha", 
            "Áustria", "Inglaterra", "Hungria", "Bélgica", "Holanda", 
            "Itália", "Azerbaijão", "Singapura", "EUA (Austin)", 
            "México", "Brasil", "Las Vegas", "Catar", "Abu Dhabi"
        ]

        # 2. Limpa o calendário antigo da temporada 2024 (caso você rode o script duas vezes)
        EtapaCalendario.objects.filter(temporada=temporada_2024).delete()

        # 3. Cria as pistas e as etapas
        for ordem, nome_pista in enumerate(calendario_oficial, start=1):
            # Cria a pista com dados genéricos caso ela não exista no banco
            pista, _ = Pista.objects.get_or_create(
                nome=nome_pista,
                defaults={
                    'pais': nome_pista,
                    'tamanho': 5.0,
                    'quantidade_voltas': 50,
                    'desgaste_pneus': 5,
                    'exigencia_motor': 5,
                    'chance_safety_car': 20
                }
            )
            
            # Vincula a pista à temporada na ordem correta
            EtapaCalendario.objects.create(
                temporada=temporada_2024,
                pista=pista,
                ordem=ordem
            )

        self.stdout.write(self.style.SUCCESS(f"Sucesso! Temporada {temporada_2024.ano} configurada com 24 etapas."))