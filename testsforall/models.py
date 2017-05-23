# encoding: utf-8
from __future__ import unicode_literals
from model_utils.managers import InheritanceManager
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core import serializers
import datetime
import hashlib
import time

from django.db import models


def _createHash():
    """This function generate 10 character long hash"""
    hash = hashlib.sha1()
    hash.update(str(time.time()))
    return  hash.hexdigest()[:-10]

class UserTests(models.Model):
    created_at = models.DateTimeField(default=datetime.datetime.now(), help_text = "Fecha de creacion")
    ROLES_CHOICES = (
            (0, "Root"),
            (1, "Admin"),
            (2, "Normal"),
        )
    role = models.IntegerField(default = 2)
    email_confirmed = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name = "UserTest", help_text = "UserTest")
    hashlink = models.CharField(max_length=10,default=_createHash,unique=True)
    friends = models.ManyToManyField('self', related_name = "friends", help_text = "Friends")
    
class FriendRequest(models.Model):
    petitioner = models.ForeignKey(UserTests, related_name = "solicitante", help_text = "Solicitante de amistad")
    requested = models.ForeignKey(UserTests, related_name = "solicitado", help_text = "Solicitado de amistad")
    daterequest = models.DateTimeField(default=datetime.datetime.now(), help_text = "Fecha de solicitud")
    accepted = models.BooleanField(default=False)
    acceptDate = models.DateTimeField(null = True, help_text = "Fecha de aceptación de amistad")
    
    
class Image(models.Model):
    image = models.FileField(null = True, upload_to = "media", help_text="Imagen de soporte.")
    uploader = models.ForeignKey(UserTests, related_name = "Uploader", help_text = "Uploader")
    
class Survey(models.Model):
    title = models.CharField(null = True, max_length = 200)
    creator = models.ForeignKey(UserTests, related_name = "User", help_text = "User")
    created_at = models.DateTimeField(default = datetime.datetime.now, help_text = "Fecha de creación")
    last_edition = models.DateTimeField(null = True, help_text = "Última edición")
    future_publication = models.DateTimeField(null = True, help_text = "Fecha de publicacion")
    future_close = models.DateTimeField(null = True, help_text = "Fecha de cierre")
    published = models.BooleanField(default = False, help_text = "Publicado")
    participants = models.ManyToManyField(UserTests, blank = True, related_name = "participants", help_text = "Participantes")
    image = models.ManyToManyField(Image, blank = True, help_text = "Imagen")
    typesurvey = models.CharField(max_length = 200)
    editors = models.ManyToManyField(UserTests, related_name = "editors", help_text = "Editores")
    objects = InheritanceManager()
    
    def getFirstImage(self):
        if self.image.all().count() != 0:
            return self.image.all()[0]
        else:
            return None

class Test(Survey):
    rules = models.CharField(null = True, max_length = 500)
    max_result = models.FloatField(null = True)
    pass

class Normal(Test):
    pass

class Limit(Test):
    limitwrong = models.IntegerField()
    
class Encuesta(Survey):
    pass

class Opinion(Encuesta):
    pass

class Personality(Encuesta):
    pass
    
class Group(models.Model):
    leader = models.ForeignKey(UserTests, related_name = "Lider", help_text= "Lider")
    title = models.CharField(null = True, max_length = 200)
    members = models.ManyToManyField(UserTests, help_text= "Miembros")
    created_at = models.DateTimeField(default = datetime.datetime.now, help_text = "Fecha de creación")
    last_edition = models.DateTimeField(null = True, help_text = "Última edición")
    
class Question(models.Model):
    title = models.CharField(null = True, max_length = 200)
    survey = models.ForeignKey(Survey, related_name = "question_set", help_text = "Test")
    image = models.ForeignKey(Image, null = True,  help_text="Imagen de soporte.")
    value = models.FloatField(null = True)
    valueminus = models.FloatField(null = True)
    objects = InheritanceManager()
    
class Multiple(Question):
    nok = models.IntegerField()
    
class MultipleWrongMinus(Multiple):
    discount = models.FloatField()
    
class Answer(models.Model):
    title = models.CharField(max_length = 200, null = True)
    correct = models.BooleanField(default = False)
    question = models.ForeignKey(Question, null = True, related_name = "answer_set", help_text = "Question")
    image = models.ForeignKey(Image, null = True,  help_text="Imagen de respuesta.")
    
class Result(models.Model):
    score = models.FloatField(default = -1)
    user = models.ForeignKey(UserTests, help_text = "Usuario que ha hecho el test")
    survey = models.ForeignKey(Survey, help_text = "Survey realizada")
    datedone = models.DateTimeField(default = datetime.datetime.now(), help_text = "Fecha de realización de test")


    
