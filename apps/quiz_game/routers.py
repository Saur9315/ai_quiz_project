from rest_framework import routers
from apps.quiz_game import views


router = routers.SimpleRouter()

router.register('quiz-questions', views.QuizApiView, basename='quiz-questions')
router.register('quiz-upload', views.QuizQuiestionUploadView, basename='quiz-upload')
router.register('quizzes', views.QuizViewSet, basename='quizzes')
