from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.quiz_game.models import Quiz, UserQuizGame, UserStats
from apps.quiz_game.ml_model import predict
from apps.quiz_game.serializers import QuizQuestionListSerializer, QuestionSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

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
    serializer_classes = [
        QuestionSerializer,
        QuizQuestionListSerializer,
    ]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizQuestionListSerializer
        elif self.action in ['retrieve',]:  # 'create', 'update', 'partial_update'
            return QuestionSerializer
        
    def get_queryset(self):
        if self.action == 'list':   # add completed quiz checkbocks
            request = self.request
            page = int(request.query_params.get('page', 1))
            page_size = 5
            offset = (page - 1) * page_size
            return Quiz.objects.all()[offset:offset + page_size]
        elif self.action == 'retrieve':
            return Quiz.objects.filter(id=self.kwargs['pk'])
        return super().get_queryset()
    
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        if not UserQuizGame.objects.filter(user=user, quiz=serializer.validated_data.get('quiz')).exists():
            UserQuizGame.objects.create(user=user, quiz=serializer.validated_data.get('quiz'))
        return super().perform_create(serializer)
    
    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        quiz = self.get_object()
        user_quiz_game = UserQuizGame.objects.get(user=request.user, quiz=quiz)
        
        given_answers = request.data.get('given_answers', [])
        user_quiz_game.given_answers = given_answers
        if len(given_answers) == len(quiz.answer_choices):
            user_quiz_game.is_completed = True
        user_quiz_game.save()
        
        # Update UserStats based on the answers
        correct_answers_count = sum(1 for i, answer in enumerate(given_answers) if answer in quiz.true_answer_indexes)
        user_stats, created = UserStats.objects.get_or_create(user=request.user)
        user_stats.total_correct_answers += correct_answers_count
        user_stats.total_xp += quiz.question_xp * correct_answers_count
        user_stats.save()
        
        return Response({"detail": "Answers submitted successfully."}, status=status.HTTP_200_OK)
    
    
