import random
from django.shortcuts import render, get_object_or_404
from .models import Equipe, Piloto, Pista

def painel_geral(request):
    minha_equipe = Equipe.objects.get(id=1)

    contexto = {
        'equipe': minha_equipe,
        'saldo': minha_equipe.orcamento
    }
    return render(request, 'simulador/painel.html', contexto)

def garagem(request):
    minha_equipe = Equipe.objects.get(id=1)
    return render(request, 'simulador/garagem.html', {'equipe': minha_equipe})


def mercado_pilotos(request):
    minha_equipe = Equipe.objects.get(id=1)
    pilotos = Piloto.objects.all()

    contexto = {
        'equipe':minha_equipe,
        'saldo': minha_equipe.orcamento,
        'pilotos': pilotos
    }

    return render(request, 'simulador/mercado.html', contexto)


def simular_corrida(request, id_pista):
    # 1. Puxamos a pista clicada e a equipe do jogador
    pista = get_object_or_404(Pista, id=id_pista)
    minha_equipe = Equipe.objects.get(id=1)
    
    # Pegamos o primeiro piloto da equipe para a simulação (você pode melhorar isso depois)
    meu_piloto = Piloto.objects.filter(equipe_atual=minha_equipe).first()
    
    # 2. Variáveis de controle da corrida
    relatorio_corrida = [] # Vai guardar o texto do que aconteceu para mostrarmos na tela
    desgaste_pneu_atual = 0.0
    status_carro = "Na Pista"
    voltas_completadas = 0

    # Verificação básica de segurança
    if not meu_piloto or not minha_equipe.motor:
        return render(request, 'simulador/erro.html', {'mensagem': 'Você precisa de um piloto e um motor antes de correr!'})

    relatorio_corrida.append(f"LARGADA! {meu_piloto.nome} acelera no GP de {pista.pais}!")

    # 3. O Loop da Corrida (Volta a volta)
    for volta in range(1, pista.quantidade_voltas + 1):
        voltas_completadas = volta
        
        # Matemática do desgaste: Abrasividade da pista aumenta o desgaste do pneu
        desgaste_pneu_atual += pista.desgaste_pneus * 1.5 
        
        # Teste 1: Confiabilidade do Motor (A exigência da pista força o motor)
        # Se a exigência bater num número maior que a confiabilidade do seu motor, ele quebra.
        chance_quebra = random.randint(1, 100) + (pista.exigencia_motor * 2)
        if chance_quebra > minha_equipe.motor.confiabilidade:
            status_carro = "FUMAÇA NO MOTOR! Abandono."
            relatorio_corrida.append(f"Volta {volta}: {status_carro}")
            break # Interrompe o laço imediatamente, o carro quebrou!

        # Teste 2: Safety Car
        chance_safety_car = random.randint(1, 100)
        if chance_safety_car <= pista.chance_safety_car:
            relatorio_corrida.append(f"Volta {volta}: ACIDENTE NA PISTA! Safety Car acionado. O ritmo diminui.")
            desgaste_pneu_atual -= 2.0 # Pneu desgasta menos com SC
            continue # Pula para a próxima volta sem checar o resto

        # Teste 3: Necessidade de Pit Stop (Controle do Manager)
        if desgaste_pneu_atual > 85.0:
            relatorio_corrida.append(f"Volta {volta}: Pneu muito desgastado ({desgaste_pneu_atual}%). Box, Box, Box!")
            desgaste_pneu_atual = 0.0 # Trocou o pneu, zera o desgaste
        
        # Se nada de grave aconteceu, registra uma volta normal de vez em quando para o log não ficar vazio
        elif volta % 10 == 0:
             relatorio_corrida.append(f"Volta {volta}: Ritmo constante. Desgaste do pneu em {desgaste_pneu_atual}%.")

    # 4. Fim da Simulação
    if status_carro == "Na Pista":
        relatorio_corrida.append(f"BANDEIRA QUADRICULADA! {meu_piloto.nome} finaliza a corrida com sucesso!")
        
        # Exemplo de premiação financeira pelo sucesso
        pagamento = 0
        if minha_equipe.patrocinadores.exists():
            for pat in minha_equipe.patrocinadores.all():
                pagamento += pat.pagamento_por_corrida
            
            minha_equipe.orcamento += pagamento
            minha_equipe.save()
            relatorio_corrida.append(f"Patrocinadores pagaram $ {pagamento} na sua conta!")

    # Empacotamos os resultados e mandamos para o HTML
    contexto = {
        'pista': pista,
        'piloto': meu_piloto,
        'relatorio': relatorio_corrida,
        'voltas_rodadas': voltas_completadas,
        'status_final': status_carro
    }
    
    return render(request, 'simulador/resultado_corrida.html', contexto)