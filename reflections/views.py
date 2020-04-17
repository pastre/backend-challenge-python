from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.db.utils import IntegrityError 

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import  logout as djangoLogout

from  .models import *

import json
import datetime

def fetchObject(obj, objId):

	try:
		ret = obj.objects.get(pk=objId)
		return ret
	except ObjectDoesNotExist:
		return False

def payload(message, status):
	return HttpResponse(
		json.dumps( {"status": status, "payload": message} if not message == None else { "status": status } )
	) 
def error(message): return payload(message, "error")
def success(message): return payload(message, "success")

def wrongMethod(): return HttpResponseForbidden('Wrong method, sorry')
def malformedRequest(): return HttpResponse(f'malformedRequest')
def authenticationNeeded(): return error("Authentication required")

# Fetches a reflection from the DB
def fetchReflection(reflectionId):
	return fetchObject(Reflection, reflectionId)

# Formats a reflection from the DB
def formattedModel(m):

		serialized = json.dumps(m.toDict())
		return HttpResponse(serialized)
def formattedModelArray(a): 
	asDict = [ i.toDict() for i in a]

	return success(asDict)
def reflectionsInRange(params):

	if not 'from' in params.keys(): return malformedRequest()
	try:
		start = datetime.datetime.strptime(params["from"][0], "%d%m%Y")
		# start = stringToDatetime(params["from"][0])

		if "to" in params.keys(): end = datetime.datetime.strptime(params["to"][0] + " 23:59:59", "%d%m%Y %H:%M:%S")
		else: end = datetime.datetime.now()

		reflections = Reflection.objects.filter(createdAt__range = (start, end))

		return formattedModelArray(reflections)
	except ValueError:
		return error("Failed to parse date")

# -------- Reflection methods
def createReflection(text): 
	newReflection = Reflection(content = text)
	newReflection.save()

	return  getReflection(newReflection.pk)
def getReflection(reflectionId):
	reflection = fetchReflection(reflectionId)

	if not reflection: return malformedRequest()

	return formattedModel(reflection)
def updateReflection(reflectionId, newReflection): pass # TODO
def deleteReflection(reflectionId): 
	reflection = fetchReflection(reflectionId)
	if not reflection: return malformedRequest()

	reflection.delete()

	return formattedModelArray(Reflection.objects.all())

@csrf_exempt 
def reflections(request, reflectionId = None):
	
	if not request.user.is_authenticated: return authenticationNeeded()

	if reflectionId == None: 
		if request.method == 'GET': 
			params = dict(request.GET)
			if len(params.keys()) == 0: return formattedModelArray(Reflection.objects.all())
			return reflectionsInRange(params)

		if request.method == 'POST': 
			content = request.POST.get("content")

			if not content: return error("porra brow")
			return createReflection(content)
		
		return wrongMethod()

	if request.method == 'GET': return getReflection(reflectionId)
	if request.method == 'DELETE': return deleteReflection(reflectionId) # TODO
	if request.method == 'PUT': pass # TODO
		
		

	return wrongMethod()

# -------- User methods
def fetchUser(userId): return fetchObject(User, userId)
def createUserIfPossible(request):
	payload = request.POST
	required = ['username', 'email', 'password',]
	
	# Se esta faltando algum parametro, retorne erro
	for req in required: 
		if not req in payload.keys(): return malformedRequest()

	username, email, password = [payload.get(i) for i in required]

	try:
		user = User.objects.create_user(username = username, email=email, password=password )
		user.save()

		return formattedModel(user)
	except IntegrityError: return error("User already exists")
def deleteUserIfPossible(userId):
	user = fetchUser(userId)

	if not user: return error("User not found!")
	user.delete()
	return formattedModel(user)
def usersInRange(params):
	if 'username' in params.keys(): 
		pattern = params["username"][0]
		users = User.objects.filter(username__contains=pattern)

		return formattedModelArray(users)
	return malformedRequest("Use the <i>username</i> parameter to search a user")

@csrf_exempt 
def users(request, userId = None):
	isAuth = request.user.is_authenticated
	# Se nao for post, retorne erro
	if userId == None:
		if request.method == 'GET': 
			if not isAuth: return authenticationNeeded()
			params = dict(request.GET)
			if len(params.keys()) == 0: return malformedRequest("Use the <i>username</i> parameter to search a user")
			return usersInRange(params)

		if request.method == 'POST': return createUserIfPossible(request)

		return wrongMethod()

	if not isAuth: return authenticationNeeded()
	if request.method == 'DELETE': return deleteUserIfPossible(userId)
	
	return wrongMethod()
	

# -------- Auth methods
@csrf_exempt
def auth(request):
	if not request.method == 'POST': wrongMethod()

	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)

	if user is not None:
		login(request, user)
		myUser = User.objects.get(pk = user.pk)
		return success({"user": myUser.toDict()})

	else: return error("Authentication failed")


@csrf_exempt
def logout(request):
	djangoLogout(request)

	return success(None)