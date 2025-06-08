import pandas as pd
from django.core.management.base import BaseCommand
from apps.quiz_game.models import Quiz

class Command(BaseCommand):
    help = 'Import quizzes from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['excel_file']
        df = pd.read_excel(file_path)

        created_count = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                topic = row['topic']
                difficulty = row['difficulty']
                question = row['question']
                xp = int(row['xp'])

                answer_choices = [row[f'answer{i}'] for i in range(1, 5)]
                print(answer_choices)
                correct_indexes = [int(i.strip()) for i in str(row['correct_answer_idx']).split(';')]

                quiz = Quiz.objects.create(
                    topic=topic,
                    difficulty=difficulty,
                    question_name=question,
                    answer_choices=answer_choices,
                    true_answer_indexes=correct_indexes,
                    question_xp=xp
                )

                created_count += 1

            except Exception as e:
                errors.append((idx, str(e)))

        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} quizzes successfully imported.'))
        if errors:
            self.stdout.write(self.style.WARNING(f'⚠️ {len(errors)} errors:'))
            for i, err in errors:
                self.stdout.write(f'Row {i + 2}: {err}')
