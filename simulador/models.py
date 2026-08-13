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
    nome = models.CharField(max_length=100, default="Minha Equipe F1")
    orcamento = models.DecimalField(max_digits=15, decimal_places=2, default=100000000.00) # $ 100 Milhões iniciais
    motor = models.ForeignKey(FornecedorMotor, on_delete=models.SET_NULL, null=True, blank=True)
    patrocinadores = models.ManyToManyField(Patrocinador, blank=True)
    controlada_pelo_jogador = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

# 3. Pilotos (Depende da Equipe)
class Piloto(models.Model):
    nome = models.CharField(max_length=50)
    sobrenome = models.CharField(max_length=50)
    numero = models.CharField(max_length=5, blank=True, null=True)
    nacionalidade = models.CharField(max_length=50, default='Desconhecida')
    habilidade = models.IntegerField(default=70) # Usado para os cálculos de salário
    
    # Relação com a equipe (Pode estar vazio se for Agente Livre)
    equipe_atual = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} {self.sobrenome} ({self.habilidade})"

    # Propriedades Dinâmicas (Não viram colunas no banco, mas ajudam na View)
    @property
    def salario(self):
        return self.habilidade * 50000

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