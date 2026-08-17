from django.db import models

# 1. Fornecedores e Patrocinadores (Básicos)
class FornecedorMotor(models.Model):
    nome = models.CharField(max_length=50) # Ex: Ferrari, Mercedes, Honda
    potencia = models.IntegerField(default=80)
    confiabilidade = models.IntegerField(default=80) 
    preco = models.DecimalField(max_digits=15, decimal_places=2, default=5000000.00)

    def __str__(self):
        return self.nome

class Patrocinador(models.Model):
    nome = models.CharField(max_length=100)
    pagamento_por_corrida = models.DecimalField(max_digits=10, decimal_places=2, default=250000.00)
    meta_posicao = models.IntegerField(default=10) # Bônus se chegar no Top 10

    def __str__(self):
        return self.nome

# 2. A Equipe do Jogador (Depende do Motor e Patrocinador)
class Equipe(models.Model):
    CATEGORIAS = (('ATUAL', 'Grid Atual'),
        ('CLASSICA', 'Equipe Clássica'),
        ('ORIGINAL', 'Criada pelo Jogador'),)
    
    nome = models.CharField(max_length=100)
    orcamento = models.DecimalField(max_digits=15, decimal_places=2, default=15000000.00) # $ 15 Milhões iniciais
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='ATUAL')
    controlada_pelo_jogador = models.BooleanField(default=False)
    pontos_campeonato = models.IntegerField(default=0)
    motor = models.ForeignKey(FornecedorMotor, on_delete=models.SET_NULL, null=True, blank=True)
    patrocinadores = models.ManyToManyField(Patrocinador, blank=True)

    def __str__(self):
        return self.nome

# 3. Pilotos (Depende da Equipe)
class Piloto(models.Model):
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    numero = models.CharField(max_length=5, blank=True, null=True)
    nacionalidade = models.CharField(max_length=50, default='Desconhecida')
    imagem_perfil = models.ImageField(upload_to='pilotos/', null=True, blank=True)
    
    # NOVOS: Atributos Específicos (Substituem a antiga "habilidade")
    ritmo_corrida = models.IntegerField(default=70)
    ritmo_classificacao = models.IntegerField(default=70)
    nivel_ataque = models.IntegerField(default=70)
    nivel_defesa = models.IntegerField(default=70)
    
    xp_acumulado = models.IntegerField(default=0)
    pontos_campeonato = models.IntegerField(default=0)
    
    equipe_atual = models.ForeignKey('Equipe', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} {self.sobrenome} (OVR: {self.overall})"

    # O overall agora é uma Propriedade Dinâmica. Ele não fica salvo como coluna no banco, 
    # ele é calculado na hora toda vez que você pedir piloto.overall
    @property
    def overall(self):
        soma = self.ritmo_corrida + self.ritmo_classificacao + self.nivel_ataque + self.nivel_defesa
        return soma // 4 

    @property
    def salario(self):
        return self.overall * 50000

    @property
    def valor_contratacao(self):
        return self.salario * 10

# 4. Pistas (Independentes)
class Pista(models.Model):
    nome = models.CharField(max_length=100)
    pais = models.CharField(max_length=50, default='Desconhecido')
    tamanho = models.FloatField(default=5.0) # Km
    quantidade_voltas = models.IntegerField(default=50)
    
    # Atributos para a mecânica do jogo
    desgaste_pneus = models.IntegerField(default=5) # 1 a 10
    exigencia_motor = models.IntegerField(default=5) # 1 a 10
    chance_safety_car = models.IntegerField(default=20) # Porcentagem

    def __str__(self):
        return f"{self.nome} - {self.pais}"


class Carro(models.Model):
    # O OneToOneField amarra 1 carro para 1 equipe (se a equipe for deletada, o carro some)
    equipe = models.OneToOneField(Equipe, on_delete=models.CASCADE)
    aerodinamica = models.IntegerField(default=40)
    chassi_peso = models.IntegerField(default=40)
    
    def __str__(self):
        return f"Carro da {self.equipe.nome}"


class Temporada(models.Model):
    ano = models.IntegerField(default = 2026)
    etapa_atual = models.IntegerField(default=1)

    def __str__(self):
        return f"Temporada {self.ano} Etapa {self.etapa_atual}"


class EtapaCalendario(models.Model):
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name='corridas')
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE)
    ordem = models.IntegerField()

    def __str__(self):
        return f"Etapa {self.ordem}: {self.pista.nome} ({self.temporada.ano})"


class Noticias(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    temporada_relacionada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    etapa_publicacao = models.IntegerField(default=1)

    def __str__(self):
        return self.titulo