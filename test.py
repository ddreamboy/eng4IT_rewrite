import re
import time

message = {
    'context': 'Обсуждение повышения эффективности обработки данных с использованием контейнеров.',
    'translation': 'Discussion about improving data processing efficiency using containers.',
    'messages': [
        {
            'author': 'Sarah (Senior Dev)',
            'text': 'Привет! Мы испытываем некоторые узкие места в нашем конвейере обработки данных. Текущий процесс очистки данных занимает слишком много времени. Есть идеи, как это ускорить?',
            'translation': "Hey! We're experiencing some bottlenecks in our data processing pipeline. The current Data Cleaning process is taking too long. Any ideas on how to expedite this?",
            'is_user_message': False,
        },
        {
            'author': 'You',
            'text': 'Мы определенно можем улучшить ситуацию. Я думаю, что использование {gap1} может значительно помочь. Мы можем разбить процесс и запустить его параллельно {gap2}.',
            'translation': 'We could definitely improve things. I think using {gap1} could significantly help. We can break down the process and run it in parallel {gap2}.',
            'is_user_message': True,
            'gaps': [
                {
                    'id': 1,
                    'correct': 'Container',
                    'correct_translation': 'контейнеров',
                    'options': [
                        {'word': 'Container', 'translation': 'контейнеров'},
                        {'word': 'Data Cleaning', 'translation': 'очистки данных'},
                        {
                            'word': 'Virtual Machines',
                            'translation': 'виртуальных машин',
                        },
                        {'word': 'Databases', 'translation': 'баз данных'},
                    ],
                },
                {
                    'id': 2,
                    'correct': 'in a timely manner',
                    'correct_translation': 'своевременно',
                    'options': [
                        {
                            'word': 'in a timely manner',
                            'translation': 'своевременно',
                        },
                        {
                            'word': 'for further clarification',
                            'translation': 'для дальнейшего уточнения',
                        },
                        {'word': 'expedite', 'translation': 'ускорить'},
                        {'word': 'sequentially', 'translation': 'последовательно'},
                    ],
                },
            ],
        },
        {
            'author': 'Sarah (Senior Dev)',
            'text': 'Звучит многообещающе! Давайте обсудим это подробнее. Можешь подготовить краткий план для дальнейшего уточнения реализации?',
            'translation': "That sounds promising! Let's discuss this further. Could you prepare a brief proposal for further clarification on the implementation?",
            'is_user_message': False,
        },
        {
            'author': 'You',
            'text': 'Конечно, я могу подготовить предложение, в котором будут изложены преимущества и потенциальный план реализации. Я постараюсь передать его вам {gap3}.',
            'translation': "Sure, I can prepare a proposal outlining the benefits and a potential implementation plan. I'll aim to get it to you {gap3}.",
            'is_user_message': True,
            'gaps': [
                {
                    'id': 3,
                    'correct': 'in a timely manner',
                    'correct_translation': 'своевременно',
                    'options': [
                        {
                            'word': 'in a timely manner',
                            'translation': 'своевременно',
                        },
                        {
                            'word': 'for further clarification',
                            'translation': 'для дальнейшего уточнения',
                        },
                        {'word': 'expedite', 'translation': 'ускорить'},
                        {'word': 'later today', 'translation': 'позже сегодня'},
                    ],
                }
            ],
        },
        {
            'author': 'Sarah (Senior Dev)',
            'text': 'Отлично, спасибо! Дай знать, если тебе что-нибудь ещё понадобится.',
            'translation': 'Great, thanks! Let me know if you need anything else.',
            'is_user_message': False,
        },
    ],
    'metrics': {
        'technical_terms_count': 4,
        'complex_words_count': 3,
        'difficulty_score': 0.6,
        'grammar_complexity': 0.5,
    },
}


def letter_print(text, delay=0.01):
    for letter in text:
        print(letter, end='', flush=True)
        time.sleep(delay)
    print()


messages = message['messages']
prepositions = [
    'in',
    'on',
    'at',
    'for',
    'with',
    'by',
    'about',
    'of',
    'to',
    'from',
    'as',
    'into',
    'like',
    'through',
    'after',
    'over',
    'between',
    'out',
    'against',
    'during',
    'without',
    'before',
    'under',
    'around',
    'among',
    'down',
    'along',
    'off',
    'above',
    'near',
    'up',
    'out',
    'behind',
    'beyond',
    'inside',
    'beneath',
    'beside',
    'between',
    'beneath',
    'towards',
    'onto',
    'within',
    'beneath',
    'behind',
    'across',
    'inside',
]
articles = ['a', 'an', 'the']


def get_user_input(gap):
    """Функция для получения ввода пользователя и проверки правильности."""
    print('\nВыберите правильный вариант:')
    for idx, option in enumerate(gap['options'], start=1):
        print(f'{idx}. {option["word"]} - {option["translation"]}')

    while True:
        user_input = input('Введите номер правильного варианта: ').strip()
        if user_input.isdigit():
            user_input = int(user_input)
            if 1 <= user_input <= len(gap['options']):
                selected_option = gap['options'][user_input - 1]['word']
                return selected_option
            else:
                print('Некорректный номер. Попробуйте еще раз.')
        else:
            print('Пожалуйста, введите номер варианта.')


def process_message(message):
    """Функция для обработки сообщения."""
    if message['is_user_message']:
        translation_by_words = message['translation'].split()
        text_by_words = message['text'].split()  # Разбиваем русский текст на слова
        sentence = []
        translation_sentence = []
        i = 0
        while i < len(translation_by_words):
            word = translation_by_words[i]
            if '{gap' in word:
                # Используем регулярное выражение для извлечения ID пропуска
                gap_match = re.search(r'\{gap(\d+)\}', word)
                if gap_match:
                    gap_id = int(gap_match.group(1))  # Извлекаем ID пропуска
                    # Находим соответствующий пропуск в списке gaps
                    gap = next(g for g in message['gaps'] if g['id'] == gap_id)

                    # Выводим текущее предложение до пропуска
                    print('\n')
                    print(message['author'])
                    letter_print(' '.join(sentence) + ' ...', delay=0.01)
                    print('Перевод:', ' '.join(translation_sentence) + ' ...')

                    # Получаем ввод пользователя
                    user_input = get_user_input(gap)
                    while user_input != gap['correct']:
                        print(
                            f'Неверный ответ. Правильный ответ: {gap["correct"]} - {gap["correct_translation"]}'
                        )
                        user_input = get_user_input(gap)

                    # Добавляем правильный ответ в предложение
                    sentence.append(gap['correct'])
                    translation_sentence.append(gap['correct_translation'])
                    i += 1  # Переходим к следующему слову
                else:
                    # Если не удалось извлечь ID, просто добавляем слово как есть
                    sentence.append(word)
                    translation_sentence.append(text_by_words[i])
                    i += 1
            else:
                sentence.append(word)
                translation_sentence.append(text_by_words[i])
                i += 1

        # После обработки всех слов выводим оставшийся текст разом
        print('\n')
        print(message['author'])
        letter_print(' '.join(sentence), delay=0.01)
        print('Перевод:', ' '.join(translation_sentence))
    else:
        # Если это не сообщение пользователя, просто выводим его
        print('\n')
        print(message['author'])
        letter_print(message['translation'], delay=0.01)
        print('Перевод:', message['text'])


# Основной цикл программы
messages = message['messages']
for msg in messages:
    process_message(msg)
