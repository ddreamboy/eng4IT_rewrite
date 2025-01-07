import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
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
    settings = Column(JSON, default=dict)  # Для хранения пользовательских настроек
    learning_preferences = Column(JSON, default=dict)  # Предпочтения в обучении

    # Статистика
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)

    # Индексы
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_activity', 'is_active', 'last_login'),
    )

    # Связи
    learning_attempts = relationship(
        'LearningAttempt',
        backref='user',
        primaryjoin='UserORM.id == LearningAttempt.user_id',
        lazy='dynamic',  # Для оптимизации запросов
    )


class TermORM(Base):
    """Модель для технических терминов"""

    __tablename__ = 'terms'

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False, unique=True)
    primary_translation = Column(String, nullable=False)
    category_main = Column(String, nullable=False)
    category_sub = Column(String)
    difficulty = Column(String, nullable=False)
    definition_en = Column(String, nullable=False)
    definition_ru = Column(String, nullable=False)
    example_en = Column(String)
    example_context = Column(String)
    related_terms = Column(JSON, default=list)
    alternate_translations = Column(JSON, default=list)

    # Индексы для ускорения поиска
    __table_args__ = (
        Index('idx_terms_term', 'term'),  # Для поиска по термину
        Index(
            'idx_terms_category', 'category_main', 'category_sub'
        ),  # Для фильтрации по категориям
        Index('idx_terms_difficulty', 'difficulty'),  # Для фильтрации по сложности
    )

    # Попытки изучения
    learning_attempts = relationship(
        'LearningAttempt',
        back_populates='term',
        primaryjoin='and_(LearningAttempt.item_id == TermORM.id, '
        'LearningAttempt.item_type == "term")',
        foreign_keys='[LearningAttempt.item_id]',
    )


class WordORM(Base):
    """Модель для общих слов"""

    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False, unique=True)
    translation = Column(String, nullable=False)
    context = Column(String)
    context_translation = Column(String)
    word_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)

    # Индексы
    __table_args__ = (
        Index('idx_words_word', 'word'),  # Для поиска по слову
        Index(
            'idx_words_type_difficulty', 'word_type', 'difficulty'
        ),  # Для фильтрации по типу и сложности
    )

    # Попытки изучения
    learning_attempts = relationship(
        'LearningAttempt',
        back_populates='word',
        primaryjoin='and_(LearningAttempt.item_id == WordORM.id, '
        'LearningAttempt.item_type == "word")',
        foreign_keys='[LearningAttempt.item_id]',
    )


class TaskContext(Base):
    """Модель для хранения контекстов заданий"""

    __tablename__ = 'task_contexts'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    context_type = Column(String, nullable=False)
    target_item_id = Column(Integer, nullable=False)
    target_item_type = Column(Enum(ItemType), nullable=False)
    wrong_options = Column(JSON)
    difficulty = Column(String)

    # Индексы
    __table_args__ = (
        Index(
            'idx_context_type_item',
            'context_type',
            'target_item_type',
            'target_item_id',
        ),  # Для поиска контекстов
        Index(
            'idx_context_difficulty', 'difficulty'
        ),  # Для фильтрации по сложности
    )

    attempts = relationship('LearningAttempt', back_populates='context')


class LearningAttempt(Base):
    """Модель для хранения всех попыток изучения"""

    __tablename__ = 'learning_attempts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    task_type = Column(String, nullable=False)
    context_id = Column(Integer, ForeignKey('task_contexts.id'))
    is_successful = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Индексы
    __table_args__ = (
        Index('idx_attempts_user', 'user_id'),  # Для поиска по пользователю
        Index(
            'idx_attempts_item', 'item_type', 'item_id'
        ),  # Для поиска по изучаемому элементу
        Index('idx_attempts_task', 'task_type'),  # Для анализа по типу задания
        Index('idx_attempts_date', 'created_at'),  # Для временного анализа
    )

    # Связи
    context = relationship('TaskContext', back_populates='attempts')
    term = relationship(
        'TermORM',
        foreign_keys=[item_id],
        primaryjoin='and_(LearningAttempt.item_id == TermORM.id, '
        'LearningAttempt.item_type == "term")',
    )
    word = relationship(
        'WordORM',
        foreign_keys=[item_id],
        primaryjoin='and_(LearningAttempt.item_id == WordORM.id, '
        'LearningAttempt.item_type == "word")',
    )


"""
Как добавить новый тип задания:

1. Создать новый контекст в TaskContext:
   context = TaskContext(
       text="Текст задания",
       context_type="new_task_type",
       target_item_id=term_id,
       target_item_type=ItemType.TERM,
       wrong_options=[...],
       difficulty="intermediate"
   )

2. Записать попытки выполнения:
   attempt = LearningAttempt(
       user_id=user_id,
       item_id=term_id,
       item_type=ItemType.TERM,
       task_type="new_task_type",
       context_id=context.id,
       is_successful=True/False
   )

Примеры анализа:

1. Общий прогресс по слову/термину:
   attempts = session.query(LearningAttempt).filter(
       LearningAttempt.item_id == item_id,
       LearningAttempt.item_type == item_type
   ).all()
   success_rate = sum(1 for a in attempts if a.is_successful) / len(attempts)

2. Прогресс по типу задания:
   attempts = session.query(LearningAttempt).filter(
       LearningAttempt.task_type == task_type
   ).all()
   
3. Сложные контексты:
   contexts = session.query(TaskContext).join(LearningAttempt).group_by(
       TaskContext.id
   ).having(
       func.avg(case([(LearningAttempt.is_successful, 1)], else_=0)) < 0.5
   ).all()

4. Динамика обучения:
   attempts = session.query(
       LearningAttempt.created_at,
       func.avg(case([(LearningAttempt.is_successful, 1)], else_=0))
   ).group_by(
       func.date(LearningAttempt.created_at)
   ).order_by(
       LearningAttempt.created_at
   ).all()
"""
