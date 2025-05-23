def preprocess_input(user_data: dict):
    return [
        user_data.get('true_answers', 0),
        user_data.get('total_questions', 0),
        user_data.get('xp', 0),
    ]
