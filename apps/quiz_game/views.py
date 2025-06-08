from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.quiz_game.models import Quiz, UserQuizGame, UserStats, QuizResult
from apps.quiz_game.ml_model import predict
from apps.quiz_game.serializers import (
    QuizQuestionListSerializer, 
    QuestionSerializer, 
    QuizStartSerializer, 
    QuizSubmitSerializer,
    QuizResultSerializer,
    QuizResultHistorySerializer,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, BooleanFilter, CharFilter

from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
import pandas as pd

from django.db.models import Avg, Sum, Count
from collections import Counter


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


class QuizFilter(FilterSet):
    topic = CharFilter(field_name='topic', lookup_expr='exact')
    difficulty = CharFilter(field_name='difficulty', lookup_expr='exact')
    only_uncompleted = BooleanFilter(method='filter_uncompleted')

    def filter_uncompleted(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            completed = QuizResult.objects.filter(user=self.request.user).values_list('quiz_id', flat=True)
            queryset = queryset.exclude(id__in=completed)
        return queryset

    class Meta:
        model = Quiz
        fields = ['topic', 'difficulty', 'only_uncompleted']


class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuizFilter

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
    
    @action(detail=False, methods=['get'], url_path='my-progress')
    def my_progress(self, request):
        user = request.user
        results = QuizResult.objects.filter(user=user)

        total_quizzes = results.count()
        total_xp = results.aggregate(Sum('xp_earned'))['xp_earned__sum'] or 0
        avg_correct_percent = 0

        topic_counter = Counter()
        topic_correctness = {}

        if total_quizzes > 0:
            total_questions = 0
            total_correct = 0
            for r in results:
                total_questions += len(r.quiz.true_answer_indexes)
                total_correct += r.correct_count

                topic = r.quiz.topic
                topic_counter[topic] += 1

                if topic not in topic_correctness:
                    topic_correctness[topic] = {'correct': 0, 'total': 0}
                topic_correctness[topic]['correct'] += r.correct_count
                topic_correctness[topic]['total'] += len(r.quiz.true_answer_indexes)

            avg_correct_percent = round((total_correct / total_questions) * 100, 2)

        top_topics = sorted(
            topic_correctness.items(),
            key=lambda x: (x[1]['correct'] / x[1]['total']) if x[1]['total'] else 0,
            reverse=True
        )[:3]

        worst_topics = sorted(
            topic_correctness.items(),
            key=lambda x: (x[1]['correct'] / x[1]['total']) if x[1]['total'] else 0,
        )[:3]

        return Response({
            'user': user.username,
            'total_quizzes_passed': total_quizzes,
            'total_xp_earned': total_xp,
            'avg_accuracy_percent': avg_correct_percent,
            'top_topics': [
                {
                    'topic': topic,
                    'accuracy_percent': round((v['correct'] / v['total']) * 100, 2)
                } for topic, v in top_topics
            ],
            'weakest_topics': [
                {
                    'topic': topic,
                    'accuracy_percent': round((v['correct'] / v['total']) * 100, 2)
                } for topic, v in worst_topics
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request):
        leaderboard_data = (
            QuizResult.objects.values('user__id', 'user__username')
            .annotate(total_xp=Sum('xp_earned'))
            .order_by('-total_xp')[:10]  # топ-10
        )

        return Response(leaderboard_data)


class QuizResultViewSet(ReadOnlyModelViewSet):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user)
    

class MyQuizHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = QuizResult.objects.filter(user=request.user).order_by('-created_at')
        serializer = QuizResultHistorySerializer(results, many=True)
        return Response(serializer.data)
    

# Quiz Excel Upload View
class QuizExcelUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "No file uploaded."}, status=400)

        try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                Quiz.objects.create(
                    topic=row['topic'],
                    difficulty=row['difficulty'],
                    question_name=row['question'],
                    answer_choices=[row['answer1'], row['answer2'], row['answer3'], row['answer4']],
                    true_answer_indexes=[int(i.strip()) for i in str(row['correct_answer_idx']).split(';')],
                    question_xp=int(row['xp'])
                )

            return Response({"status": "Quiz data uploaded successfully."})

        except Exception as e:
            return Response({"error": str(e)}, status=500)