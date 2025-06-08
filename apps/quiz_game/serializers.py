from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from apps.quiz_game.models import Quiz, UserQuizGame, UserStats, QuizResult


class QuestionSerializer(ModelSerializer):
    answer_choices = serializers.ListField(
        child=serializers.CharField(), min_length=1
    )
    true_answer_indexes = serializers.ListField(
        child=serializers.IntegerField(), min_length=1
    )

    class Meta:
        model = Quiz
        fields = [
            'id',
            'topic',
            'question_name',
            'answer_choices',
            'true_answer_indexes',  # hide
            'difficulty',
            'question_xp',
        ]
    
    def validate(self, data):
        answers = data['answer_choices']
        indexes = data['true_answer_indexes']

        for index in indexes:
            if index >= len(answers) or index < 0:
                raise serializers.ValidationError(
                    f"Index {index} is out of bounds for answer_choices"
                )
        return data

class QuizQuestionListSerializer(ModelSerializer):
    # questions = SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'topic', 'question_name',]

    # def get_question(self, obj):
    #     request = self.context.get('request')
    #     # print("the obj: ", obj)
    #     # page = int(request.query_params.get('page', 1))
    #     # page_size = 5
    #     # offset = (page-1)*page_size
    #     # questions = obj.question.all()[offset:offset+page_size]
    #     return self.get_questions(obj)
    #     # return QuestionSerializer(questions, many=True).data

class QuizStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'topic', 'question_name', 'answer_choices', 'difficulty', 'question_xp']


class QuizSubmitSerializer(serializers.Serializer):
    submitted_answers = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = '__all__'
        read_only_fields = ['user', 'quiz', 'submitted_at']
