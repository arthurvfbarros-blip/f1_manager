import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Equipe, Piloto, Pista

def painel_geral(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')

    contexto = {
        'equipe': minha_equipe,
        'saldo': minha_equipe.orcamento
    }
    return render(request, 'simulador/painel.html', contexto)

def garagem(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')
    return render(request, 'simulador/garagem.html', {'equipe': minha_equipe})


def mercado_pilotos(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')
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
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')
    
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


def novo_jogo(request):
    if request.method == 'POST':
        # Lógica para quando o jogador clica em "Assumir Equipe"
        equipe_id = request.POST.get('equipe_id')
        equipe_escolhida = Equipe.objects.get(id=equipe_id)
        
        # Limpa o controle de qualquer outra equipe e assume a nova
        Equipe.objects.all().update(controlada_pelo_jogador=False)
        equipe_escolhida.controlada_pelo_jogador = True
        equipe_escolhida.save()
        
        return redirect('painel_geral')

    # Se for GET, apenas exibe a tela organizada
    contexto = {
        'equipes_atuais': Equipe.objects.filter(categoria='ATUAL'),
        'equipes_classicas': Equipe.objects.filter(categoria='CLASSICA'),
    }
    return render(request, 'simulador/novo_jogo.html', contexto)


def processar_mercado_ia():
    equipes_ia = Equipe.objects.filter(controlada_pelo_jogador=False)
    
    for equipe in equipes_ia:
        pilotos_atuais = Piloto.objects.filter(equipe_atual=equipe)
        
        # 1. A equipe só vai ao mercado buscar titular se estiver com vaga sobrando
        if pilotos_atuais.count() < 2:
            # ... lógica de contratar o melhor disponível
            continue

        # 2. A Troca Oportuna (Anti-Camaleão)
        # A IA só demite um piloto se o substituto disponível for pelo menos 5 pontos MELHOR em Overall
        melhor_agente_livre = Piloto.objects.filter(equipe_atual__isnull=True).order_by('-habilidade').first()
        
        if melhor_agente_livre:
            for piloto in pilotos_atuais:
                # TRAVA 1: O piloto atual tem que estar indo mal (Ex: Overall menor que 80)
                # TRAVA 2: O agente livre tem que ser BEM melhor (Margem de +5)
                # TRAVA 3: A equipe tem que ter o dobro do dinheiro do passe (Não gasta tudo de uma vez)
                
                if piloto.overall < 80 and (melhor_agente_livre.overall >= piloto.overall + 5):
                    if equipe.orcamento >= (melhor_agente_livre.valor_contratacao * 2):
                        
                        # Efetua a troca cirúrgica
                        equipe.orcamento -= melhor_agente_livre.valor_contratacao
                        equipe.save()
                        
                        # Demite o antigo e assina com o novo
                        piloto.equipe_atual = None
                        piloto.save()
                        
                        melhor_agente_livre.equipe_atual = equipe
                        melhor_agente_livre.save()
                        break # Para não trocar os dois pilotos de uma vez


def avancar_tempo(request):
    # Aqui vamos processar tudo que acontece na passagem do tempo
    
    # 1º A IA faz as trocas dela se precisar
    processar_mercado_ia() 
    
    # 2º Pagamos os salários? (Você pode adicionar isso depois)
    
    messages.success(request, "Uma semana se passou. O mercado e as equipes se movimentaram.")
    
    # Recarrega o painel geral para ver se algo mudou
    return redirect('painel_geral')