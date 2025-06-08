from django.urls import path, include
from .routers import router
from .views import MyQuizHistoryView


urlpatterns = [
    path('', include(router.urls)),
    path('my-quiz-history/', MyQuizHistoryView.as_view(), name='my-quiz-history'),
]