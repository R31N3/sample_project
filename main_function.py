# coding: utf-8
from __future__ import unicode_literals
from little_fuctions import *

aliceAnswers = read_answers_data("data/answers_dict_example")


def choice_wrd(last_char, used_words):
    if type(used_words) is not list:
        used_words = []
    from random import choice
    user_word = choice(read_answers_data("data/words")[last_char])
    while user_word in used_words:
        user_word = choice(read_answers_data("data/words")[last_char])
    return user_word


# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message):  # ща будет магия
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def handle_dialog(request, response, user_storage, database):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    user_word = input_message.split()
    if request.is_new_session:
        if not database.get_entry(request.user_id):
            output_message = "Привет-привет. Не хочешь ли ты сыграть в слова? Если да, то просто назови своё имя!"
        else:
            output_message = "И снова здравствуй! Продолжим игру??"
            user_storage = {'suggests': [
                "Продолжить",
                "Начать сначала"
            ]}
        return message_return(response, user_storage, output_message)

    if input_message in ['не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        output_message = choice(aliceAnswers["quitTextVariations"])
        response.end_session = True
        return message_return(response, user_storage, output_message)

    if not database.get_entry(request.user_id):
        database.add_user(request.user_id)
        output_message = "Что ж, я тебя запомню. Начнем?"
        user_storage = {'suggests': [
            "Давай"
        ]}
        return message_return(response, user_storage, output_message)

    if "таблица лидеров" in input_message or "лидеры" in input_message:
        # leaders = database.get_leaders()
        # Получение таблицы лидеров, нужно получать лист, как снизу, да, именно так.
        leaders = [(1, "Дима бох", 1487), (99999999, "Гоша лох", 0)]
        output_message = "Имеющиеся на данный момент лидеры:\n{}\n".format(
            ",\n".join(["{} место - {}, счет - {}".format(i[0], i[1], i[2]) for i in
                        leaders])) + "Продолжим игру или начнем сначала?"
        user_storage = {'suggests': [
            "Продолжить",
            "Начать сначала"
        ]}
        return message_return(response, user_storage, output_message)

    entry = database.get_entry(request.user_id)[0]
    data = (entry[1], entry[2], database.get_words(request.user_id))
    if "продолжить" in input_message or "давай" in input_message or "сначала" in input_message or (
            "хочу" in input_message and "не" in input_message) and not data[1]:
        chosen_word = choice_wrd(data[1] if data[1] else choice("айцукенгшщзхфывапролджэячсмитбю"))
        if "сначала" in input_message:
            print(data[2])
            database.update(request.user_id, chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2])
        else:
            database.update(request.user_id, chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2])
        output_message = "Только запомни, учитываться будет только первое слово. Что ж, начнём! Внимание, слово " \
                         "- {}.".format(chosen_word)
        user_storage = {'suggests': []}
        return message_return(response, user_storage, output_message)

    elif data and data[1]:
        if user_word[0][0].lower() == data[1]:
            if check_wrd(user_word[0]):
                used_words = data[2]
                if user_word[0] not in used_words:
                    used_words.append(user_word[0])
                    chosen_word = choice_wrd(user_word[0][-1] if user_word[0][-1] not in "ьъ" else user_word[0][-2],
                                             used_words)
                    output_message = "Правильно! Следующее слово - {}".format(chosen_word)
                    database.update(request.user_id,
                                    chosen_word[-1] if chosen_word[-1] not in "ьъ" else chosen_word[-2])
                    database.add_word(request.user_id, user_word[0])
                else:
                    output_message = "Неправильно, это слово уже использовалось!"
            else:
                output_message = "Неправильно, ты это слово выдумал, что ли?"
        else:
            output_message = "Неправильно! Слово начинается не с той буквы, напоминаю, должна быть буква {}"\
                .format(data[1])
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
