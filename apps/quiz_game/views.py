from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.quiz_game.models import Quiz, UserQuizGame, UserStats
from apps.quiz_game.ml_model import predict
from apps.quiz_game.serializers import QuizQuestionListSerializer, QuestionSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# @login_required
# def profile_prediction_view(request):
#     user_data = {
#         "true_answers": 16,
#         "total_questions": 20,
#         "xp": 480,
#     }
#     level = predict.predict_knowledge_level(user_data)
#     return render(request, 'result.html', {'level': level})

class QuizApiView(ModelViewSet):
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
