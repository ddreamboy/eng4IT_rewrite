import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ItemType(enum.Enum):
    TERM = 'term'
    WORD = 'word'


class DifficultyLevel(enum.Enum):
    BEGINNER = 'beginner'
    BASIC = 'basic'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'


class TaskType(enum.Enum):
    WORD_TRANSLATION = 'word_translation'  # Перевод слова
    TERM_DEFINITION = 'TERM_DEFINITION' # Выбор определения
    CONTEXT = 'context'  # Заполнение пропуска в контексте
    WORD_MATCHING = 'word_matching'  # Сопоставление слов/определений
    WRITE = 'write'  # Написание слова по определению
    CHAT_DIALOG = 'chat_dialog'
    EMAIL_STRUCTURE = 'email_structure'


class AchievementType(enum.Enum):
    STREAK = 'streak'  # Достижения за регулярность
    COMPLETION = 'completion'  # За выполнение определенного числа заданий
    MASTERY = 'mastery'  # За достижение определенного уровня мастерства
    SPEED = 'speed'  # За скорость выполнения
    ACCURACY = 'accuracy'  # За точность выполнения
    CATEGORY = 'category'  # За прогресс в определенной категории


class WordType(enum.Enum):
    NOUN = 'NOUN'
    VERB = 'VERB'
    ADJECTIVE = 'ADJECTIVE'
    ADVERB = 'ADVERB'
    PHRASAL_VERB = 'PHRASAL_VERB'
    COMMON_PHRASE = 'COMMON_PHRASE'


class UserORM(Base):
    """Модель пользователя системы"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Настройки пользователя
    settings = Column(JSON, default=dict)
    learning_preferences = Column(JSON, default=dict)

    # Уровень и прогресс
    current_level = Column(
        Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE
    )
    proficiency_score = Column(Float, default=50.0)  # Общая метрика уровня (0-100)
    daily_goal = Column(Integer, default=20)
    study_streak = Column(Integer, default=0)

    # Статистика
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)

    __table_args__ = (
        CheckConstraint('proficiency_score >= 0 AND proficiency_score <= 100'),
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_activity', 'is_active', 'last_login'),
    )

    # Связи
    learning_attempts = relationship(
        'LearningAttempt',
        back_populates='user',
        lazy='selectin',
    )
    word_statuses = relationship(
        'UserWordStatus',
        back_populates='user',  # Изменено с 'backref' на 'back_populates'
    )


class Achievement(Base):
    """Модель для описания возможных достижений"""

    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    achievement_type = Column(Enum(AchievementType), nullable=False)

    # Условия для получения достижения в JSON формате
    # Примеры:
    # {"type": "streak", "days": 7}
    # {"type": "completion", "count": 100, "task_type": "translation"}
    # {"type": "mastery", "level": 90, "category": "databases"}
    # {"type": "speed", "time": 30, "task_type": "matching"}
    conditions = Column(JSON, nullable=False)

    # Уровни достижения (бронза, серебро, золото и т.д.)
    levels = Column(JSON, nullable=False)

    __table_args__ = (Index('idx_achievement_type', 'achievement_type'),)


class UserAchievement(Base):
    """Модель для хранения достижений пользователя"""

    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    current_level = Column(Integer, default=0)  # 0 = не получено
    progress = Column(Float, default=0.0)  # Прогресс к следующему уровню
    achieved_at = Column(DateTime)

    __table_args__ = (
        Index('idx_user_achievements', 'user_id', 'achievement_id', unique=True),
    )


class TermORM(Base):
    """Модель для технических терминов"""

    __tablename__ = 'terms'

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False, unique=True)
    primary_translation = Column(String, nullable=False)
    category_main = Column(String, nullable=False)
    category_sub = Column(String)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)
    definition_en = Column(String, nullable=False)
    definition_ru = Column(String, nullable=False)
    example_en = Column(String)
    example_context = Column(String)
    related_terms = Column(JSON, default=list)
    alternate_translations = Column(JSON, default=list)

    __table_args__ = (
        Index('idx_terms_term', 'term'),
        Index('idx_terms_category', 'category_main', 'category_sub'),
        Index('idx_terms_difficulty', 'difficulty'),
    )

    # Связи
    learning_attempts = relationship(
        'LearningAttempt',
        back_populates='term',
        primaryjoin='and_(LearningAttempt.item_id == TermORM.id, '
        'LearningAttempt.item_type == "term")',
        foreign_keys='[LearningAttempt.item_id]',
    )
    user_statuses = relationship(
        'UserWordStatus',
        primaryjoin='and_(UserWordStatus.item_id == TermORM.id, UserWordStatus.item_type == "term")',
        foreign_keys='[UserWordStatus.item_id]',
    )


class WordORM(Base):
    """Модель для общих слов"""

    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False, unique=True)
    translation = Column(String, nullable=False)
    context = Column(String)
    context_translation = Column(String)
    word_type = Column(Enum(WordType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), nullable=False)

    __table_args__ = (
        Index('idx_words_word', 'word'),
        Index('idx_words_type_difficulty', 'word_type', 'difficulty'),
    )

    # Связи
    learning_attempts = relationship(
        'LearningAttempt',
        back_populates='word',
        primaryjoin='and_(LearningAttempt.item_id == WordORM.id, '
        'LearningAttempt.item_type == "word")',
        foreign_keys='[LearningAttempt.item_id]',
        overlaps='learning_attempts',
    )

    user_statuses = relationship(
        'UserWordStatus',
        primaryjoin='and_(UserWordStatus.item_id == WordORM.id, UserWordStatus.item_type == "word")',
        foreign_keys='[UserWordStatus.item_id]',
        overlaps='user_statuses',
    )


class UserWordStatus(Base):
    """Модель для отслеживания прогресса пользователя по словам/терминам"""

    __tablename__ = 'user_word_status'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)

    # Статусы
    is_favorite = Column(Boolean, default=False)
    is_known = Column(Boolean, default=False)
    mastery_level = Column(Float, default=0.0)

    # SRS поля
    last_reviewed = Column(DateTime)
    next_review_date = Column(DateTime)
    ease_factor = Column(Float, default=2.5)
    interval_level = Column(Integer, default=0)

    __table_args__ = (
        CheckConstraint('ease_factor >= 1.3 AND ease_factor <= 3.0'),
        CheckConstraint('mastery_level >= 0 AND mastery_level <= 100'),
        Index(
            'idx_user_word_status', 'user_id', 'item_id', 'item_type', unique=True
        ),
        Index('idx_next_review', 'user_id', 'next_review_date'),
    )

    user = relationship('UserORM', back_populates='word_statuses')  # Добавлено


class TaskContext(Base):
    """Модель для хранения контекстов заданий"""

    __tablename__ = 'task_contexts'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    context_type = Column(Enum(TaskType), nullable=False)
    target_item_id = Column(Integer, nullable=False)
    target_item_type = Column(Enum(ItemType), nullable=False)

    # JSON поля для разных типов заданий
    options = Column(
        JSON
    )  # Может содержать: неправильные ответы, варианты для сопоставления и т.д.
    task_metadata = Column(
        JSON
    )  # Дополнительные данные специфичные для типа задания

    difficulty = Column(Enum(DifficultyLevel))

    __table_args__ = (
        Index(
            'idx_context_type_item',
            'context_type',
            'target_item_type',
            'target_item_id',
        ),
        Index('idx_context_difficulty', 'difficulty'),
    )

    attempts = relationship('LearningAttempt', back_populates='context')


class LearningAttempt(Base):
    """Модель для хранения всех попыток изучения"""

    __tablename__ = 'learning_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    context_id = Column(Integer, ForeignKey('task_contexts.id'))

    # Результат
    is_successful = Column(Boolean, nullable=False)
    score = Column(Float)  # Для заданий с градацией успеха (например, matching)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_attempts_user', 'user_id'),
        Index('idx_attempts_item', 'item_type', 'item_id'),
        Index('idx_attempts_task', 'task_type'),
        Index('idx_attempts_date', 'created_at'),
    )

    # Связи
    context = relationship('TaskContext', back_populates='attempts')
    term = relationship(
        'TermORM',
        foreign_keys=[item_id],
        primaryjoin='and_(LearningAttempt.item_id == TermORM.id, '
        'LearningAttempt.item_type == "term")',
        back_populates='learning_attempts',
        overlaps="learning_attempts,word"
    )
    word = relationship(
        'WordORM',
        foreign_keys=[item_id],
        primaryjoin='and_(LearningAttempt.item_id == WordORM.id, '
        'LearningAttempt.item_type == "word")',
        back_populates='learning_attempts',
        overlaps="learning_attempts,term"
    )

    timing = relationship('TaskTiming', uselist=False, back_populates='attempt')
    user = relationship(
        'UserORM',
        back_populates='learning_attempts',
        foreign_keys=[user_id],
    )


class TaskTiming(Base):
    """Модель для хранения времени выполнения заданий"""

    __tablename__ = 'task_timings'

    id = Column(Integer, primary_key=True)
    attempt_id = Column(
        Integer, ForeignKey('learning_attempts.id'), nullable=False
    )
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Дополнительные метрики времени
    thinking_time = Column(Integer)  # время на обдумывание в миллисекундах
    input_time = Column(Integer)  # время на ввод ответа
    total_time = Column(Integer)  # общее время

    attempt = relationship('LearningAttempt', back_populates='timing')

    __table_args__ = (
        Index('idx_task_timing_attempt', 'attempt_id'),
        CheckConstraint('end_time > start_time'),
    )


"""
Добавление нового типа задания в систему
========================================

1. Добавить новый тип в TaskType enum:
---------------------------------------
class TaskType(enum.Enum):
    TRANSLATION = 'translation'
    NEW_TASK = 'new_task'  # Добавляем новый тип


2. Создание задания в базе:
---------------------------

А. Базовое задание с выбором ответа:
-----------------------------------
context = TaskContext(
    text="What is the correct translation of 'database'?",
    context_type=TaskType.TRANSLATION,
    target_item_id=term.id,
    target_item_type=ItemType.TERM,
    difficulty=term.difficulty,
    options={
        'wrong_options': ['файл', 'таблица', 'программа'],
        'correct_option': 'база данных'
    }
)

Б. Задание на сопоставление (matching):
-------------------------------------
context = TaskContext(
    text="Match the terms with their definitions",
    context_type=TaskType.MATCHING,
    target_item_id=term.id,
    target_item_type=ItemType.TERM,
    difficulty=term.difficulty,
    options={
        'pairs': [
            {'term': 'database', 'definition': 'organized collection of data'},
            {'term': 'query', 'definition': 'request for data retrieval'},
            {'term': 'index', 'definition': 'data structure improving search speed'}
        ]
    },
    task_metadata={
        'max_score': 3,  # Количество правильных пар
        'partial_scoring': True  # Разрешаем частичные баллы
    }
)

В. Задание с свободным ответом:
------------------------------
context = TaskContext(
    text="Write the definition of a database in your own words",
    context_type=TaskType.WRITE,
    target_item_id=term.id,
    target_item_type=ItemType.TERM,
    difficulty=term.difficulty,
    task_metadata={
        'key_points': ['data storage', 'organized', 'structured', 'retrieval'],
        'min_words': 10,
        'scoring_type': 'key_points_based'
    }
)


3. Запись попытки выполнения:
----------------------------

А. Для заданий с четким правильным ответом:
-----------------------------------------
attempt = LearningAttempt(
    user_id=user.id,
    item_id=term.id,
    item_type=ItemType.TERM,
    task_type=TaskType.TRANSLATION,
    context_id=context.id,
    is_successful=True,
    score=1.0
)

Б. Для заданий с частичным успехом:
---------------------------------
attempt = LearningAttempt(
    user_id=user.id,
    item_id=term.id,
    item_type=ItemType.TERM,
    task_type=TaskType.MATCHING,
    context_id=context.id,
    is_successful=matching_score >= 0.7,  # Успех, если набрано 70% баллов
    score=matching_score  # float от 0 до 1
)

В. Для заданий с нечетким ответом:
--------------------------------
attempt = LearningAttempt(
    user_id=user.id,
    item_id=term.id,
    item_type=ItemType.TERM,
    task_type=TaskType.WRITE,
    context_id=context.id,
    is_successful=key_points_covered >= 3,  # Успех, если раскрыто достаточно ключевых моментов
    score=calculate_writing_score(response, context.metadata)
)


4. Обновление прогресса пользователя:
-----------------------------------
async def update_user_progress(
    session: AsyncSession,
    user_id: int,
    item_id: int,
    item_type: ItemType,
    score: float
):
    # Получаем или создаем статус слова для пользователя
    status = await get_or_create_word_status(session, user_id, item_id, item_type)
    
    # Обновляем уровень освоения
    status.mastery_level = calculate_new_mastery_level(
        current_level=status.mastery_level,
        attempt_score=score
    )
    
    # Обновляем SRS параметры
    status.last_reviewed = datetime.utcnow()
    status.interval_level += 1 if score >= 0.8 else 0
    status.ease_factor = calculate_new_ease_factor(
        current_factor=status.ease_factor,
        score=score
    )
    status.next_review_date = calculate_next_review_date(
        interval_level=status.interval_level,
        ease_factor=status.ease_factor,
        score=score
    )
    
    # Обновляем общий уровень пользователя
    user = await session.get(UserORM, user_id)
    user.proficiency_score = await calculate_overall_proficiency(
        session, user_id
    )
    
    await session.commit()


5. Примеры вспомогательных функций:
---------------------------------
def calculate_new_mastery_level(current_level: float, attempt_score: float) -> float:
    weight = 0.3  # Вес нового результата
    return min(100, current_level * (1 - weight) + attempt_score * 100 * weight)

def calculate_next_review_date(
    interval_level: int,
    ease_factor: float,
    score: float
) -> datetime:
    if interval_level == 0:
        days = 1
    else:
        base_interval = [1, 3, 7, 14, 30][min(interval_level - 1, 4)]
        days = base_interval * ease_factor * (0.8 + (score * 0.4))
    
    return datetime.utcnow() + timedelta(days=days)

async def calculate_overall_proficiency(
    session: AsyncSession,
    user_id: int
) -> float:
    # Получаем все статусы слов пользователя
    statuses = await session.execute(
        select(UserWordStatus).filter_by(user_id=user_id)
    )
    
    # Вычисляем средний уровень освоения
    total_mastery = 0
    count = 0
    for status in statuses.scalars():
        total_mastery += status.mastery_level
        count += 1
    
    return total_mastery / count if count > 0 else 50.0  # Дефолтное значение
"""