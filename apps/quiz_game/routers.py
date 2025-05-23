from rest_framework import routers
from apps.quiz_game import views


router = routers.SimpleRouter()

router.register('quiz-questions', views.QuizApiView, basename='quiz-questions')