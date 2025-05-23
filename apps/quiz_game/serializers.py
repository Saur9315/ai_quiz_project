from rest_framework.serializers import ModelSerializer, SerializerMethodField
from apps.quiz_game.models import Quiz, UserQuizGame, UserStats


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Quiz
        fields = [
            'id',
            'topic',
            'question_name',
            'answer_choices',
            'true_answer_indexes'  # hide
            # 'difficulty',
            # 'question_xp',
        ]

class QuizQuestionListSerializer(ModelSerializer):
    questions = SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'question_name',]

    def get_question(self, obj):
        request = self.context.get('request')
        page = int(request.query_params.get('page', 1))
        page_size = 5
        offset = (page-1)*page_size
        questions = obj.questions.all()[offset:offset+page_size]
        return QuestionSerializer(questions, many=True).data