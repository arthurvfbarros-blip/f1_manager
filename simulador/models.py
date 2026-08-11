from django.db import models

class Piloto(models.Model):
        nome = models.CharField(max_length=50)
        sobrenome = models.CharField(max_length=50)
        numero = models.CharField(max_length=5, blank = True, null = True)
        nacionalidade = models.CharField(max_length=50)

        def __str__(self):
            return f"{self.nome} {self.sobrenome} - {self.numero}"

class Pista(models.Model):
      nome = models.CharField(max_length=50)
      pais = models.CharField(max_length=50)
      tamanho = models.CharField(max_length=10, blank=True, null = True)
      quantidade_voltas = models.CharField(max_length=5, blank=True, null = True)

      def __str__(self):
            return f"{self.nome}, pais: {self.pais}, tamanho:{self.tamanho}, voltas: {self.quantidade_voltas}"

class FornecedorMotor(models.Model):
      nome = models.CharField(max_length=50)
      potencia = models.IntegerField()
      confiabilidade = models.IntegerField()
      preco = models.DecimalField(max_digits=10, decimal_places=2)

class Patrocinador(models.Model):
      nome = models.CharField(max_length=100)
      pagamento_por_corrida = models.DecimalField(max_digits=10, decimal_places=2)
      meta_posicao = models.IntegerField()

class Equipe(models.Model):
      nome = models.CharField(max_length=100)
      orcamento = models.DecimalField(max_digits=15, decimal_places=2)
      motor = models.ForeignKey(FornecedorMotor, on_delete=models.SET_NULL, null=True)
      patrocinadores = models.ManyToManyField(Patrocinador)     
