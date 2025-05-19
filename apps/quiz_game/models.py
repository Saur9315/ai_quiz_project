from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model



class Quiz(models.Model):
    class Topic(models.TextChoices):
        ML = 'ml', 'Machine Learning'
        DL = 'dl', 'Deep Learning'
        AI = 'dl', 'Artificial Intelligence'
        AI_POP_CULTURE = 'ai_pop_culture', 'AI in pop-culture'
        AI_APPLICATION = 'ai_application', 'Application of AI'
        CV = 'cv', 'Computer Vision'
        NLP = 'nlp', 'Natural Language Processing'
        GENERATIVE_AI = 'gen_ai', 'Generative AI'
        STATS = 'ststs', 'Statistics'

    class Difficulty(models.TextChoices):
        BEGGINNER = 'begginer', 'Begginer Level'
        MODERATE = 'moderate', 'Moderate Level'
        ADVANCED = 'advanced', 'Advanced Level'

    topic = models.CharField(
        max_length=240, 
        choices=Topic.choices, 
        verbose_name='Topic'
    )
    question_name = models.TextField(verbose_name='Question')
    answer_choices = ArrayField(
        models.TextField(),
        size=4,
        verbose_name='Answer Choices'
    )
    true_answer_indexes = ArrayField(
        models.IntegerField(), 
        verbose_name='Indices of Correct Answers'
    )
    difficulty = models.TextField(
        max_length=100,
        choices=Difficulty.choices,
        verbose_name='question difficulty'
    )
    question_xp = models.PositiveIntegerField(verbose_name='XP', blank=True)

    def clean(self):
        if not isinstance(self.true_answer_indexes, list):
            raise ValidationError("true_answer_indexes must be a list.")
        if not isinstance(self.answer_choices, list):
            raise ValidationError("answer_choices must be a list.")
        for index in self.true_answer_indexes:
            if index >= len(self.answer_choices) or index < 0:
                raise ValidationError(f'Answer index {index} is out of range.')
            

class UserQuizGame(models.Model):
    user_id = models.ForeignKey(get_user_model, on_delete=models.SET_NULL)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.SET_NULL)
    given_answers = models.TextChoices(Quiz.answer_choices.choices, blank=True)
    is_completed = models.BooleanField(verbose_name='is completed')


class UserStats(models.Model):
    class KnowledgeLevel(models.TextChoices):
        BEGGINNER = 'begginer', 'Begginer Level'
        MODERATE = 'moderate', 'Moderate Level'
        ADVANCED = 'advanced', 'Advanced Level'

    user_id = models.ForeignKey(get_user_model, on_delete=models.CASCADE)
    total_xp = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)
    knowledge_level = models.CharField(
        max_length=100,
        choices=KnowledgeLevel.choices,
        verbose_name='Knowledge Level'
    )
