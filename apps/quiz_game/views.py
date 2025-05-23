from django.shortcuts import render
from .ml_model.predict import predict_knowledge_level
from django.contrib.auth.decorators import login_required


@login_required
def profile_prediction_view(request):
    user_data = {
        "true_answers": 16,
        "total_questions": 20,
        "xp": 480,
    }
    level = predict_knowledge_level(user_data)
    return render(request, 'result.html', {'level': level})