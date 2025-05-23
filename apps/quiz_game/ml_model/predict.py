import joblib
from .preprocess import preprocess_input

# Загрузка модели
model = joblib.load('quiz_game/ml_model/model.pkl')

def predict_knowledge_level(user_data: dict):
    X = [preprocess_input(user_data)]
    return model.predict(X)[0]
