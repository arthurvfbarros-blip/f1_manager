from django.db import models

class Piloto(models.Model):
        nome = models.CharField(max_length=50)
        sobrenome = models.CharField(max_length=50)
        numero = models.CharField(max_length=5, blank = True, null = True)
        nacionalidade = models.CharField(max_length=50)

        def __str__(self):
            return f"{self.nome} {self.sobrenome} - {self.numero}"
