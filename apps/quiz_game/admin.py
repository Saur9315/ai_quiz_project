from django.contrib import admin
from apps.quiz_game.models import Quiz, UserQuizGame, UserStats


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "question_name", "difficulty", "question_xp")
    search_fields = ("title", "question_name",)

@admin.register(UserQuizGame)
class UserQuizGameAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quiz", "is_completed")
    list_filter = ("is_completed", "quiz", "user")
    search_fields = ("user__username", "quiz__title",)

@admin.register(UserStats)
class UserStatsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_xp", "total_correct_answers", "knowledge_level")
    search_fields = ("user",)