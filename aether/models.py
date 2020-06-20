from django.db.models import Model, CharField, IntegerField, ForeignKey, DateTimeField, BooleanField, EmailField, CASCADE, ManyToManyField, OneToOneField

# Create your models here.

class Email(Model):

	content = CharField(max_length = 10000)
	createdAt = DateTimeField(null=True, blank=True, auto_now = True)