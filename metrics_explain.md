Давай разберем все метрики и их назначение:

1. **SRS Метрики (UserWordStatus):**
```python
ease_factor = Column(Float, default=2.5)
# - Диапазон: 1.3 - 3.0
# - Начальное значение: 2.5
# - Назначение: Определяет, как быстро растут интервалы повторения
# - Изменение: Уменьшается при ошибках, увеличивается при успехах
# Пример расчета:
def adjust_ease_factor(current: float, success_score: float) -> float:
    if success_score >= 0.8:
        return min(3.0, current + 0.1)
    elif success_score <= 0.3:
        return max(1.3, current - 0.2)
    return current
```

2. **Общий уровень (UserORM):**
```python
proficiency_score = Column(Float, default=50.0)
# - Диапазон: 0-100
# - Начальное значение: 50.0
# - Назначение: Общий уровень владения языком
# - Факторы влияния:
#   * Средний mastery_level всех слов
#   * Сложность изучаемых слов
#   * Регулярность занятий
# Пример расчета:
async def calculate_proficiency(session, user_id):
    # Базовые веса факторов
    MASTERY_WEIGHT = 0.6
    DIFFICULTY_WEIGHT = 0.25
    REGULARITY_WEIGHT = 0.15
    
    # Сбор метрик
    avg_mastery = await get_average_mastery(session, user_id)
    difficulty_score = await get_difficulty_score(session, user_id)
    regularity_score = await get_regularity_score(session, user_id)
    
    # Итоговый расчет
    return (
        avg_mastery * MASTERY_WEIGHT +
        difficulty_score * DIFFICULTY_WEIGHT +
        regularity_score * REGULARITY_WEIGHT
    )
```

3. **Уровень освоения слова (UserWordStatus):**
```python
mastery_level = Column(Float, default=0.0)
# - Диапазон: 0-100
# - Начальное значение: 0.0
# - Назначение: Показывает насколько хорошо усвоено конкретное слово/термин
# - Факторы влияния:
#   * Успешность выполнения заданий
#   * Регулярность повторений
#   * Сложность заданий
# Пример расчета:
def calculate_mastery(attempts, word_difficulty):
    recent_success = get_recent_success_rate(attempts)
    repetition_factor = get_repetition_factor(attempts)
    difficulty_bonus = get_difficulty_bonus(word_difficulty)
    
    return min(100, recent_success * 0.7 + 
              repetition_factor * 0.2 + 
              difficulty_bonus * 0.1)
```

4. **Настройки обучения (UserORM):**
```python
learning_preferences = Column(JSON, default=dict)
# Структура:
{
    "preferred_task_types": ["translation", "context", "matching"],
    "daily_word_goal": 20,
    "preferred_categories": ["backend", "databases", "algorithms"],
    "difficulty_preference": "adaptive",  # fixed/adaptive
    "interface_language": "ru",
    "notification_settings": {
        "daily_reminder": True,
        "streak_alert": True,
        "review_notification": True
    },
    "learning_focus": {
        "terms_ratio": 0.7,  # 70% термины, 30% общие слова
        "preferred_word_types": ["noun", "verb"]
    }
}
```

5. **Оценка попытки (LearningAttempt):**
```python
score = Column(Float)
# - Диапазон: 0-1
# - Назначение: Оценка конкретной попытки
# Примеры расчета для разных типов:
def calculate_attempt_score(task_type, result):
    if task_type == TaskType.TRANSLATION:
        return 1.0 if result.is_correct else 0.0
        
    elif task_type == TaskType.MATCHING:
        return len(result.correct_matches) / result.total_pairs
        
    elif task_type == TaskType.WRITE:
        key_points_covered = len(set(result.key_points) & 
                               set(result.answer_points))
        return key_points_covered / len(result.key_points)
```

6. **Система достижений (можно добавить):**
```python
achievements = Column(JSON, default=dict)
# Структура:
{
    "streaks": {
        "current": 5,
        "max": 15,
        "milestones": [7, 30, 100]
    },
    "words_learned": {
        "total": 150,
        "by_difficulty": {
            "beginner": 50,
            "intermediate": 80,
            "advanced": 20
        }
    },
    "badges": ["quick_learner", "consistent", "vocabulary_master"]
}
```

Все эти метрики работают вместе, создавая комплексную систему оценки прогресса. Например:
1. Успешное выполнение задания → увеличение mastery_level слова
2. Повышение mastery_level → влияние на proficiency_score
3. proficiency_score влияет на подбор следующих слов и заданий
4. ease_factor корректирует интервалы повторения в SRS

Нужно что-то уточнить или добавить другие метрики?