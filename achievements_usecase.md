```python
async def check_achievements(
    session: AsyncSession,
    user_id: int,
    attempt: LearningAttempt
) -> List[UserAchievement]:
    """Проверяет и обновляет достижения пользователя после попытки."""
    
    # Получаем все возможные достижения
    achievements = await session.execute(select(Achievement))
    new_achievements = []
    
    for achievement in achievements.scalars():
        conditions = achievement.conditions
        
        # Проверяем достижение в зависимости от его типа
        if conditions['type'] == AchievementType.STREAK:
            user = await session.get(UserORM, user_id)
            if user.study_streak >= conditions['days']:
                new_achievement = await grant_achievement(
                    session, user_id, achievement.id
                )
                if new_achievement:
                    new_achievements.append(new_achievement)
                    
        elif conditions['type'] == AchievementType.SPEED:
            if attempt.timing and attempt.timing.total_time <= conditions['time']:
                new_achievement = await grant_achievement(
                    session, user_id, achievement.id
                )
                if new_achievement:
                    new_achievements.append(new_achievement)
    
    return new_achievements

async def record_task_timing(
    session: AsyncSession,
    attempt: LearningAttempt,
    start_time: datetime,
    end_time: datetime,
    thinking_time: int = None,
    input_time: int = None
) -> TaskTiming:
    """Записывает время выполнения задания."""
    
    timing = TaskTiming(
        attempt_id=attempt.id,
        start_time=start_time,
        end_time=end_time,
        thinking_time=thinking_time,
        input_time=input_time,
        total_time=int((end_time - start_time).total_seconds() * 1000)
    )
    
    session.add(timing)
    return timing

# Пример использования:
async def process_learning_attempt(
    session: AsyncSession,
    user_id: int,
    attempt_data: dict,
    timing_data: dict
):
    # Создаем попытку
    attempt = LearningAttempt(...)
    session.add(attempt)
    await session.flush()  # Получаем id попытки
    
    # Записываем время
    timing = await record_task_timing(
        session,
        attempt,
        **timing_data
    )
    
    # Проверяем достижения
    new_achievements = await check_achievements(session, user_id, attempt)
    
    # Если есть новые достижения, можно их обработать
    for achievement in new_achievements:
        # Например, отправить уведомление пользователю
        pass
    
    await session.commit()
```