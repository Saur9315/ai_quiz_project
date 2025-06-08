from django.urls import path, include
from .routers import router
from .views import MyQuizHistoryView, QuizExcelUploadView


urlpatterns = [
    path('', include(router.urls)),
    path('my-quiz-history/', MyQuizHistoryView.as_view(), name='my-quiz-history'),
    path('admin/quiz-upload/', QuizExcelUploadView.as_view(), name='quiz-excel-upload')
]