from datetime import datetime, timedelta

from django.template.context_processors import request
from rest_framework import views, exceptions
from rest_framework.response import Response
from django.contrib.auth import authenticate
import jwt


from .models import Note

from .serializers import NoteSerializer, UserSerializer


def jwt_cookie(user_id):
    # returns cookie
    payload = {
        'id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=60),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    response = Response()
    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'jwt': token
    }
    return response


class RegisterView(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return jwt_cookie(serializer.data['id'])


class LoginView(views.APIView):

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed('Authentication failed')

        return jwt_cookie(user.id)


class LogoutView(views.APIView):


    def get(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'SUCCESS'
        }
        return response

class NotesView(views.APIView):
    # get notes for logged in user
    def get(self, request):
        notes = Note.objects.filter(user_id=NoteView.get_id(request))
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    # append logged in user id and save note
    def post(self, request):
        newdata = {'user': NoteView.get_id(request)}
        newdata.update(request.data)
        serializer = NoteSerializer(data=newdata)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NoteView(views.APIView):
    @staticmethod
    # decode jwt to find logged in user id
    def get_id(request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise exceptions.AuthenticationFailed('Failed')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Expired')
        return payload['id']

    # get instance
    def get(self, request, pk, format=None):
        notes = Note.objects.filter(user_id=self.get_id(request)).get(id=pk)
        serializer = NoteSerializer(notes)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        notes = Note.objects.filter(user_id=self.get_id(request)).get(id=pk)
        notes.delete()
        return Response({'MESSAGE': 'SUCCESS'})

    # swap completed true/false
    def put(self, request, pk, format=None):
        notes = Note.objects.filter(user_id=self.get_id(request)).get(id=pk)
        notes.completed = not notes.completed
        notes.save()
        return Response({'MESSAGE': 'SUCCESS'})

    # edit note
    def post(self, request, pk, format=None):
        note = Note.objects.filter(user_id=self.get_id(request)).get(id=pk)
        note.title = request.data['title']
        note.text = request.data['text']
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data)
