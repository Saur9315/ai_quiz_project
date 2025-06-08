from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.quiz_game.models import Quiz, UserQuizGame, UserStats, QuizResult
from apps.quiz_game.ml_model import predict
from apps.quiz_game.serializers import (
    QuizQuestionListSerializer, 
    QuestionSerializer, 
    QuizStartSerializer, 
    QuizSubmitSerializer,
    QuizResultSerializer
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
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

class QuizApiView(ModelViewSet):    # for user
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizQuestionListSerializer
        elif self.action in ['retrieve',]:  # 'create', 'update', 'partial_update'
            print("Retrieving serializer for action:", self.action)
            return QuestionSerializer
        print("No serializer found for action:", self.action)
        return QuestionSerializer
        # return Exception("No serializer found for this action.")
        
    def get_queryset(self):
        print(f"Getting queryset for: {self.action}")
        if self.action == 'list':   # add completed quiz checkbocks
            print("Listing: ")
            request = self.request
            print(f"Request: {request}")
            page = int(request.query_params.get('page', 1))
            page_size = 5
            offset = (page - 1) * page_size
            print(f"Objects: {Quiz.objects.all()}")
            serializer = self.get_serializer_class()
            print(f"Serializer: {serializer}")
            
            return Quiz.objects.all()[offset:offset + page_size]
        elif self.action == 'retrieve':
            return Quiz.objects.filter(id=self.kwargs['pk'])
        return super().get_queryset()
    
    def perform_retrieve(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        if not UserQuizGame.objects.filter(user=user, quiz=serializer.validated_data.get('quiz')).exists():
            UserQuizGame.objects.create(user=user, quiz=serializer.validated_data.get('quiz'))
        return super().perform_retrieve(serializer)
    
    # @action(detail=True, methods=['post'])
    # def submit_answers(self, request, pk=None):
    #     quiz = self.get_object()
    #     user_quiz_game = UserQuizGame.objects.get(user=request.user, quiz=quiz)
        
    #     given_answers = request.data.get('given_answers', [])
    #     user_quiz_game.given_answers = given_answers
    #     if len(given_answers) == len(quiz.questions.all()):
    #         user_quiz_game.is_completed = True
    #     user_quiz_game.save()
        
    #     # Update UserStats based on the answers
    #     correct_answers_count = sum(1 for i, answer in enumerate(given_answers) if answer in quiz.true_answer_indexes)
    #     user_stats, created = UserStats.objects.get_or_create(user=request.user)
    #     user_stats.total_correct_answers += correct_answers_count
    #     user_stats.total_xp += quiz.question_xp * correct_answers_count
    #     user_stats.save()
        
    #     return Response({"detail": "Answers submitted successfully."}, status=status.HTTP_200_OK)
    

class QuizQuiestionUploadView(ModelViewSet):    # for admin, staff
    queryset = Quiz.objects.all()
    form_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuestionSerializer

    @action(detail=True, methods=['get'])
    def start(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizStartSerializer(quiz)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submitted = serializer.validated_data['submitted_answers']
        correct = quiz.true_answer_indexes

        correct_set = set(correct)
        submitted_set = set(submitted)
        correct_count = len(correct_set & submitted_set)
        total_correct = len(correct_set)

        score = int((correct_count / total_correct) * quiz.question_xp)
        result = QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            submitted_answers=submitted,
            correct_count=correct_count,
            xp_earned=score
        )

        return Response({
            'quiz_id': quiz.id,
            'correct_count': correct_count,
            'total_correct': total_correct,
            'xp_earned': score
        })
    

class QuizResultViewSet(ReadOnlyModelViewSet):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user)