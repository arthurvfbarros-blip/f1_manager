import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Equipe, Piloto, Pista, FornecedorMotor, Carro, Temporada, EtapaCalendario

def painel_geral(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')

    temporada = Temporada.objects.first()
    proxima_etapa = None
    if temporada:
        proxima_etapa = EtapaCalendario.objects.filter(temporada=temporada, ordem=temporada.etapa_atual).first()

    contexto = {
        'equipe': minha_equipe,
        'saldo': minha_equipe.orcamento,
        'temporada': temporada,
        'proxima_etapa': proxima_etapa
    }
    return render(request, 'simulador/painel.html', contexto)

def garagem(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')
        
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'treinar_piloto':
            piloto_id = request.POST.get('piloto_id')
            atributo = request.POST.get('atributo')
            custo = 500000
            
            if minha_equipe.orcamento >= custo:
                piloto = get_object_or_404(Piloto, id=piloto_id, equipe_atual=minha_equipe)
                if atributo == 'ritmo_corrida' and piloto.ritmo_corrida < 99:
                    piloto.ritmo_corrida += 1
                elif atributo == 'ritmo_classificacao' and piloto.ritmo_classificacao < 99:
                    piloto.ritmo_classificacao += 1
                elif atributo == 'nivel_ataque' and piloto.nivel_ataque < 99:
                    piloto.nivel_ataque += 1
                elif atributo == 'nivel_defesa' and piloto.nivel_defesa < 99:
                    piloto.nivel_defesa += 1
                else:
                    messages.error(request, "Atributo inválido ou no nível máximo.")
                    return redirect('garagem')
                    
                piloto.save()
                minha_equipe.orcamento -= custo
                minha_equipe.save()
                messages.success(request, f"Treinamento de {atributo} concluído para {piloto.nome}!")
            else:
                messages.error(request, "Orçamento insuficiente para treinar.")
        return redirect('garagem')

    meus_pilotos = Piloto.objects.filter(equipe_atual=minha_equipe)
    return render(request, 'simulador/garagem.html', {'equipe': minha_equipe, 'meus_pilotos': meus_pilotos, 'saldo': minha_equipe.orcamento})


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

def contratar_piloto(request, piloto_id):
    if request.method == 'POST':
        minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
        if not minha_equipe:
            return redirect('novo_jogo')
            
        piloto = get_object_or_404(Piloto, id=piloto_id)
        
        # Check if the team already has 2 drivers
        pilotos_atuais = Piloto.objects.filter(equipe_atual=minha_equipe).count()
        if pilotos_atuais >= 2:
            messages.error(request, "Sua equipe já possui 2 pilotos. Demita um antes de contratar.")
            return redirect('mercado_pilotos')
            
        if minha_equipe.orcamento >= piloto.valor_contratacao:
            minha_equipe.orcamento -= piloto.valor_contratacao
            minha_equipe.save()
            
            # Remove from previous team if any
            piloto.equipe_atual = minha_equipe
            piloto.save()
            
            messages.success(request, f"Piloto {piloto.nome} {piloto.sobrenome} contratado com sucesso!")
        else:
            messages.error(request, "Orçamento insuficiente para contratar este piloto.")
            
    return redirect('mercado_pilotos')


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

    # 5. Avançar a temporada e mercado IA
    temporada = Temporada.objects.first()
    if temporada:
        temporada.etapa_atual += 1
        temporada.save()
        
    processar_mercado_ia()

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
        
        return redirect('setup_equipe')

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
        agentes_livres = list(Piloto.objects.filter(equipe_atual__isnull=True))
        melhor_agente_livre = sorted(agentes_livres, key=lambda p: p.overall, reverse=True)[0] if agentes_livres else None
        
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

def setup_equipe(request):
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    if not minha_equipe:
        return redirect('novo_jogo')
        
    carro, _ = Carro.objects.get_or_create(equipe=minha_equipe)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'comprar_motor':
            motor_id = request.POST.get('motor_id')
            if motor_id:
                motor = get_object_or_404(FornecedorMotor, id=motor_id)
                if minha_equipe.orcamento >= motor.preco:
                    minha_equipe.orcamento -= motor.preco
                    minha_equipe.motor = motor
                    minha_equipe.save()
                    messages.success(request, f"Motor {motor.nome} adquirido por ${motor.preco}!")
                else:
                    messages.error(request, "Orçamento insuficiente para esse motor.")
                    
        elif acao == 'upgrade_aero':
            custo = 1000000
            if minha_equipe.orcamento >= custo and carro.aerodinamica < 100:
                minha_equipe.orcamento -= custo
                carro.aerodinamica += 5
                minha_equipe.save()
                carro.save()
                messages.success(request, "Aerodinâmica melhorada com sucesso!")
            else:
                messages.error(request, "Orçamento insuficiente ou nível máximo atingido.")
                
        elif acao == 'upgrade_chassi':
            custo = 1000000
            if minha_equipe.orcamento >= custo and carro.chassi_peso < 100:
                minha_equipe.orcamento -= custo
                carro.chassi_peso += 5
                minha_equipe.save()
                carro.save()
                messages.success(request, "Chassi melhorado com sucesso!")
            else:
                messages.error(request, "Orçamento insuficiente ou nível máximo atingido.")
                
        elif acao == 'demitir_piloto':
            piloto_id = request.POST.get('piloto_id')
            piloto = get_object_or_404(Piloto, id=piloto_id)
            piloto.equipe_atual = None
            piloto.save()
            messages.success(request, f"Piloto {piloto.nome} demitido!")
            
        elif acao == 'finalizar_setup':
            return redirect('painel_geral')
            
        return redirect('setup_equipe')

    contexto = {
        'equipe': minha_equipe,
        'saldo': minha_equipe.orcamento,
        'carro': carro,
        'motores': FornecedorMotor.objects.all(),
        'meus_pilotos': Piloto.objects.filter(equipe_atual=minha_equipe),
    }
    return render(request, 'simulador/setup_equipe.html', contexto)

def fim_de_semana_hub(request, id_pista):
    pista = get_object_or_404(Pista, id=id_pista)
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    
    session_key = f'weekend_{id_pista}'
    if session_key not in request.session:
        # Determine if it's a sprint weekend
        is_sprint = pista.pais in ['Brasil', 'Áustria', 'Catar', 'Estados Unidos', 'China']
        
        request.session[session_key] = {
            'is_sprint': is_sprint,
            'tl1_done': False,
            'tl2_done': False,
            'tl3_done': False if not is_sprint else True, # If sprint, skip TL3
            'sprint_quali_done': False if is_sprint else True,
            'sprint_done': False if is_sprint else True,
            'quali_done': False,
            'corrida_done': False,
        }
        request.session.modified = True
        
    estado = request.session[session_key]
    
    contexto = {
        'pista': pista,
        'estado': estado,
        'equipe': minha_equipe,
    }
    return render(request, 'simulador/fim_de_semana.html', contexto)

def sessao_simulacao(request, id_pista, tipo_sessao):
    pista = get_object_or_404(Pista, id=id_pista)
    minha_equipe = Equipe.objects.filter(controlada_pelo_jogador=True).first()
    
    session_key = f'weekend_{id_pista}'
    if session_key not in request.session:
        return redirect('fim_de_semana_hub', id_pista=id_pista)
        
    estado = request.session[session_key]
    
    # Para sessões de treinos e classificação
    if tipo_sessao != 'corrida' and tipo_sessao != 'sprint':
        estado[tipo_sessao + '_done'] = True
        request.session.modified = True
        
        pilotos = Piloto.objects.filter(equipe_atual__isnull=False)
        resultados = []
        base_time = 80.0 + random.uniform(0, 2)
        for p in pilotos:
            t = base_time + (100 - p.overall) * 0.1 + random.uniform(-0.5, 0.5)
            resultados.append({'piloto': p, 'tempo': t})
            
        resultados = sorted(resultados, key=lambda x: x['tempo'])
        
        contexto = {
            'pista': pista,
            'tipo_sessao': tipo_sessao,
            'resultados': resultados,
        }
        return render(request, 'simulador/sessao_resultado.html', contexto)
        
    # Para CORRIDA principal ou sprint
    race_key = f'race_{id_pista}_{tipo_sessao}'
    total_voltas = pista.quantidade_voltas if tipo_sessao == 'corrida' else pista.quantidade_voltas // 3
    
    if race_key not in request.session:
        pilotos = Piloto.objects.filter(equipe_atual__isnull=False)
        race_state = {
            'volta_atual': 0,
            'total_voltas': total_voltas,
            'pilotos': [],
            'log': []
        }
        for p in pilotos:
            race_state['pilotos'].append({
                'id': p.id,
                'nome': f"{p.nome} {p.sobrenome}",
                'overall': p.overall,
                'equipe': p.equipe_atual.nome if p.equipe_atual else 'Sem Equipe',
                'is_player': p.equipe_atual == minha_equipe,
                'tempo_total': 0.0,
                'desgaste_pneu': 0.0,
                'pitstops': 0,
                'status': 'Na Pista'
            })
        request.session[race_key] = race_state
        request.session.modified = True
    
    race_state = request.session[race_key]
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        voltas_a_avancar = 1
        
        if acao == 'avancar_5':
            voltas_a_avancar = 5
        elif acao == 'avancar_todas':
            voltas_a_avancar = race_state['total_voltas'] - race_state['volta_atual']
        elif acao == 'box':
            piloto_box_id = int(request.POST.get('piloto_id'))
            for rp in race_state['pilotos']:
                if rp['id'] == piloto_box_id and rp['status'] == 'Na Pista':
                    rp['desgaste_pneu'] = 0.0
                    rp['tempo_total'] += 22.0
                    rp['pitstops'] += 1
                    race_state['log'].insert(0, f"Volta {race_state['volta_atual']}: {rp['nome']} fez um Pit Stop (22s).")
        
        if acao in ['avancar', 'avancar_5', 'avancar_todas']:
            for v in range(voltas_a_avancar):
                if race_state['volta_atual'] >= race_state['total_voltas']:
                    break
                    
                race_state['volta_atual'] += 1
                
                for rp in race_state['pilotos']:
                    if rp['status'] != 'Na Pista':
                        continue
                        
                    base_lap = 85.0
                    lap_time = base_lap + (100 - rp['overall']) * 0.05 + (rp['desgaste_pneu'] / 100.0) * 3.0 + random.uniform(-0.5, 0.5)
                    rp['tempo_total'] += lap_time
                    rp['desgaste_pneu'] += pista.desgaste_pneus * 1.5
                    
                    if not rp['is_player'] and rp['desgaste_pneu'] > 85.0:
                        rp['desgaste_pneu'] = 0.0
                        rp['tempo_total'] += 22.0
                        rp['pitstops'] += 1
                        race_state['log'].insert(0, f"Volta {race_state['volta_atual']}: {rp['nome']} fez Pit Stop.")
                        
                    chance_quebra = random.randint(1, 1500)
                    if chance_quebra <= 2:
                        rp['status'] = "ABANDONO"
                        race_state['log'].insert(0, f"Volta {race_state['volta_atual']}: PROBLEMA COM {rp['nome']}! Abandono.")
                        
            # Ordenar por tempo
            race_state['pilotos'] = sorted(race_state['pilotos'], key=lambda x: (x['status'] != 'Na Pista', x['tempo_total']))
            
            # Checar se finalizou
            if race_state['volta_atual'] >= race_state['total_voltas']:
                if tipo_sessao == 'corrida':
                    estado['corrida_done'] = True
                    temporada = Temporada.objects.first()
                    if temporada:
                        temporada.etapa_atual += 1
                        temporada.save()
                    processar_mercado_ia()
                else:
                    estado['sprint_done'] = True
                request.session.modified = True
                
        request.session.modified = True
            
    # Calcular intervalos na UI
    for i, rp in enumerate(race_state['pilotos']):
        if i == 0:
            rp['intervalo'] = "Líder"
        elif rp['status'] != 'Na Pista':
            rp['intervalo'] = "OUT"
        else:
            diff = rp['tempo_total'] - race_state['pilotos'][i-1]['tempo_total']
            rp['intervalo'] = f"+{diff:.3f}s"
            
    player_drivers = [p for p in race_state['pilotos'] if p['is_player']]
    
    contexto = {
        'pista': pista,
        'race_state': race_state,
        'player_drivers': player_drivers,
        'is_finished': race_state['volta_atual'] >= race_state['total_voltas'],
        'tipo_sessao': tipo_sessao
    }
    return render(request, 'simulador/corrida_interativa.html', contexto)