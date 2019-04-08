# coding: utf-8
from __future__ import unicode_literals
import json
from little_fuctions import *

aliceAnswers = read_answers_data("data/answers_dict_example")

def choice_wrd():
    from random import choice
    return choice(["вотсловонабуквур", "нуещёсловонабуквуи", "словонабуквун", "огоэтослова"])
# Ну вот эта функция всем функциям функция, ага. Замена постоянному формированию ответа, ага, экономит 4 строчки!!
def message_return(response, user_storage, message):
    # ща будет магия
    response.set_text(message)
    response.set_tts(message)
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def handle_dialog(request, response, user_storage):
    from random import choice
    if not user_storage:
        user_storage = {"suggests": []}
    input_message = request.command.lower()
    # первый запуск/перезапуск диалога
    if request.is_new_session:
        output_message = "Привет-привет. Не хочешь ли ты сыграть в слова?"
        user_storage = {'suggests': [
            "Давай"
        ]}
        return message_return(response, user_storage, output_message)

    print("!"+input_message)
    if input_message in ['не хочется', 'в следующий раз', 'выход', "не хочу", 'выйти']:
        output_message = choice(aliceAnswers["quitTextVariations"])
        response.end_session = True
        return message_return(response, user_storage, output_message)
    print(user_storage)
    if "давай" in input_message or ("хочу" in input_message and "не" in input_message) and "last_bukovka"\
            not in user_storage.keys():
        wrd = choice_wrd()
        user_storage[request.user_id] = {"answer": wrd[-1], "score": 0}
        output_message = "Только запомни, учитываться будет только первое слово. Что ж, начнём! Внимание, слово " \
                         "- {}.".format(wrd)
        user_storage = {'suggests': []}
        return message_return(response, user_storage, output_message)

    elif user_storage[request.user_id]["last_bukovka"]:
        print(input_message.split())
        if input_message.split()[0][-1] == user_storage[request.user_id]["last_bukovka"]:
            wrd = choice_wrd()
            if check_wrd(wrd):
                output_message = "Правильно! Следующее слово - {}".format(wrd)
                user_storage[request.user_id]["last_bukovka"] = wrd[-1]
            else:
                output_message = "Неправильно, ты это слово выдумал, что ли?"
        else:
            output_message = "Неправильно! Слово начинается не с той буквы, напоминаю, должна быть буква {}".format(
                user_storage[request.user_id]["last_bukovka"])
        return message_return(response, user_storage, output_message)
    buttons, user_storage = get_suggests(user_storage)
    return IDontUnderstand(response, user_storage, aliceAnswers["cantTranslate"])
