from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    auteur = models.CharField(max_length=100,default="inconnu")
    genre =  models.CharField(max_length=50, default="non spécifié")
    fichier = models.FileField(upload_to='uploads/', null=True, blank=True)
    telecharges_par = models.ManyToManyField(User, blank=True, related_name="articles_telecharges")


    def __str__(self):
        return self.titre

class Meta:
    app_label= 'blog'