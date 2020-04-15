from django.db.models import Model, CharField, IntegerField, ForeignKey, DateTimeField, DecimalField, EmailField, CASCADE
from django.contrib.postgres.fields import ArrayField

class Reflection(Model):
	content = CharField(max_length = 10000)
	createdAt = DateTimeField(null=True, blank=True, auto_now = True)

	def toDict(self):
		return  {
			"id": self.pk,
			"content": self.content,
			"createdAt": self.createdAt.timestamp(),

		}