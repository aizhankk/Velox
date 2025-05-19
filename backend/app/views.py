from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.utils import timezone

from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import requests
import json
import datetime
import re

from openai import OpenAI

from .models import Task, GoogleCredentials, UserAccount, Category
from .serializers import CategorySerializer, UserTimeSerializer, TaskSerializer


class CategoryViewSet(viewsets.ModelViewSet):  
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class UpdateUserTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserTimeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Time updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TaskViewSet(viewsets.ModelViewSet):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticated]


  filter_backends = [filters.SearchFilter, filters.OrderingFilter]
  search_fields = ['title', 'category', 'notes']
  ordering_fields = ['date', 'time_start', 'created_at']

  def perform_create(self, serializer):
      task = serializer.save(user=self.request.user)

      try:
          creds_data = GoogleCredentials.objects.get(user=self.request.user)
      except GoogleCredentials.DoesNotExist:
          print("❌ Нет Google токенов для пользователя.")
          return

      creds = Credentials(
          token=creds_data.access_token,
          refresh_token=creds_data.refresh_token,
          token_uri=creds_data.token_uri,
          client_id=creds_data.client_id,
          client_secret=creds_data.client_secret,
          scopes=creds_data.scopes.split(',')
      )

      if creds.expired and creds.refresh_token:
          try:
              creds.refresh(Request())
              creds_data.access_token = creds.token
              creds_data.token_expiry = creds.token_expiry or creds.expiry
              creds_data.save()
          except Exception as e:
              print("❌ Ошибка при обновлении токена:", str(e))
              raise

      try:
          create_event_in_google_calendar(task, creds.token)
          print(f"✅ Событие создано в Google Calendar для задачи {task.title}")
      except Exception as e:
          print(f"❌ Ошибка при создании события в Google Calendar: {str(e)}")
          raise 




class OpenAITextProcessView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsAuthenticated]

  def post(self, request):
      user_text = request.data.get('text')
      if not user_text:
          return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)

      prompt = f"""
  ```

  Extract task data in JSON format with fields:
  title, category, date (YYYY-MM-DD), time_start (HH:MM:SS), time_end (HH:MM:SS), reminder (true/false), location, notes, frequency

  Text:
  {user_text}

  Respond with ONLY a valid JSON object without any markdown code blocks or additional text.
  """


      client = OpenAI(api_key=settings.OPENAI_API_KEY)

      try:
          completion = client.chat.completions.create(
              model="gpt-4o-mini",
              messages=[{"role": "user", "content": prompt}],
              temperature=0,
              max_tokens=300,
          )
          response_text = completion.choices[0].message.content.strip()

          cleaned_text = re.sub(r"```jsons*|s*```", "", response_text).strip()

          try:
              parsed_data = json.loads(cleaned_text)
          except json.JSONDecodeError:
              return Response({"error": "Invalid JSON from OpenAI", "raw_response": response_text}, status=500)

          return Response(parsed_data)

      except Exception as e:
          return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GoogleOAuthInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                }
            },
            scopes=settings.GOOGLE_OAUTH_SCOPES,
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
        )

        request.session['google_oauth_state'] = state
        return Response({'auth_url': authorization_url})



class GoogleAuthAndroidCallbackView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            code = body.get('code')
            if not code:
                return HttpResponseBadRequest("Missing 'code'")
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")
        
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': '',  # Для Android обычно пусто
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return HttpResponseBadRequest(response.text)

        tokens = response.json()
        # Здесь сохраняете токены в БД или возвращаете клиенту
        return JsonResponse(tokens)



class SaveGoogleTokensView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        token_uri = 'https://oauth2.googleapis.com/token'
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        scopes = 'openid,email,profile,https://www.googleapis.com/auth/calendar'
        expiry_date = timezone.now() + datetime.timedelta(seconds=expires_in)

        if not access_token or not refresh_token:
            return Response({'error': 'Tokens are required'}, status=status.HTTP_400_BAD_REQUEST)

        GoogleCredentials.objects.update_or_create(
            user=user,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expiry': expiry_date,
                'token_uri': token_uri,
                'client_id': client_id,
                'client_secret': client_secret,
                'scopes': scopes,
            }
        )

        return Response({'message': 'Google tokens saved successfully'})

