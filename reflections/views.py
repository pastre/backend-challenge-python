from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from  .models import *


def formattedModel(m):

		serialized = serializers.serialize('json', m)
		return HttpResponse(serialized)

def getAllReflections(): return formattedModel(Reflection.objects.all())
def deleteReflection(reflectionId): pass # TODO
def updateReflection(reflectionId, newReflection): pass # TODO

def getReflection(reflectionId):
		reflection = Reflection.objects.get(pk=reflectionId).first()
		return formattedModel(reflection)

def createReflection(text): pass # TODO


def reflections(request, reflectionId = None):
	if reflectionId == None: 
		if request.method == 'GET': return getAllReflections()
		if request.method == 'DELETE': deleteReflection(reflectionId) # TODO
		if request.method == 'POST': updateReflection(reflectionId) # TODO

		return HttpResponseForbidden('Wrong method, sorry')

		

	if request.method == 'GET': # Se tem id e é um GET, 
		try:
			return getReflection(reflectionId)
		except ObjectDoesNotExist:
			# TODO
			return HttpResponse(f'PEGUEI')


	if request.method == 'PUT':
		return createReflection()

	return HttpResponseForbidden('Wrong method, sorry')