import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Загрузка датасета
df = pd.read_excel('datasets/df_game_data.xlsx')
print(df.shape)

print(df.head())
# # Признаки и цель (измени под свой датасет)
# X = df[['true_answers', 'total_questions', 'xp']]  # или efficiency, block/task encoding
# y = df['knowledge_level']  # Целевая переменная: low / medium / high

# # Разделение на train/test
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Обучение модели
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X_train, y_train)

# # Оценка качества
# y_pred = model.predict(X_test)
# print(classification_report(y_test, y_pred))

# # Сохранение модели
# joblib.dump(model, 'quiz_game/ml_model/model.pkl')
# print("Модель сохранена в model.pkl")
