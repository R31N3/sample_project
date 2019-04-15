# coding: utf-8
from __future__ import unicode_literals
import json
from little_fuctions import *

aliceAnswers = read_answers_data("data/answers_dict_example")


def choice_wrd(chr):
    from random import choice
    user_word = choice(get_dict_from_file_str("data/user_words.txt")[chr])
    return user_word


# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message):
    # ща будет магия
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
    # первый запуск/перезапуск диалога
    if request.is_new_session:
        if not database.get_entry(request.user_id):
            output_message = "Привет-привет. Не хочешь ли ты сыграть в слова?"
            database.add_user(request.user_id)
        else:
            output_message = "И снова здравствуй! Не хочешь ли ты сыграть в слова?"
        user_storage = {'suggests': [
            "Давай"
        ]}
        return message_return(response, user_storage, output_message)

    if input_message in ['не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        output_message = choice(aliceAnswers["quitTextVariations"])
        response.end_session = True
        return message_return(response, user_storage, output_message)

    data = database.get_entry(request.user_id)[0]
    if "давай" in input_message or ("хочу" in input_message and "не" in input_message) and not data[1]:
        wrd = choice_wrd(data[1] if data[1] else choice("айцукенгшщзхфывапролджэячсмитбю"))
        database.update(request.user_id, wrd[-1] if wrd[-1] not in "ьъ" else wrd[-2], "")
        output_message = "Только запомни, учитываться будет только первое слово. Что ж, начнём! Внимание, слово " \
                         "- {}.".format(wrd)
        user_storage = {'suggests': []}
        return message_return(response, user_storage, output_message)

    elif data and data[1]:
        if user_word[0][0].lower() == data[1]:
            if check_wrd(user_word[0]):
                wrd = choice_wrd(user_word[0][-1] if user_word[0][-1] not in "ьъ" else user_word[0][-2])
                output_message = "Правильно! Следующее слово - {}".format(wrd)
                database.update(request.user_id, wrd[-1] if wrd[-1] not in "ьъ" else wrd[-2], "")
            else:
                output_message = "Неправильно, ты это слово выдумал, что ли?"
        else:
            output_message = "Неправильно! Слово начинается не с той буквы, напоминаю, должна быть буква {}".format(
                data[1])
        return message_return(response, user_storage, output_message)

    buttons, user_storage = get_suggests(user_storage)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
