def timer(executable_function):  # декоратор, честно скопированный с habrahabr.ru и чуток доделанный
    import time

    def decorate(*args, **kwargs):
        time_point = time.time()
        result = executable_function(*args, **kwargs)
        print('Время выполнения функции "{}": {:f} секунд'
              .format(executable_function.__name__, time.time() - time_point))
        return result
    return decorate


def smart_timeout(timeout: int = 0.34):
    import time

    def wrap(executable_function):
        def decorate(*args, **kwargs):
            start_time = time.time()
            result = executable_function(*args, **kwargs)
            if time.time() - start_time < timeout:
                time.sleep(timeout - (time.time() - start_time))
            return result
        return decorate
    return wrap


def error_protection(executable_function):
    import time

    def decorate(*args, **kwargs):
        try:
            result = executable_function(*args, **kwargs)
        except Exception as exc:
            print("==========\nError:\n{}\nDate: {}\n=========="
                  .format(exc, time.strftime("%H.%M.%S - %d.%m.%Y", time.localtime())))
        else:
            return result
    return decorate


def get_suggests(user_storage):
    if "suggests" in user_storage.keys():
        suggests = []
        for suggest in user_storage['suggests']:
            if type(suggest) != list:
                suggests.append({'title': suggest, 'hide': True})
            else:
                print(suggest)
                suggests.append({'title': suggest[0], "url": suggest[1], 'hide': False})
                print(suggests)
    else:
        suggests = []

    return suggests, user_storage


def IDontUnderstand(response, user_storage, answer):
    import random
    message = random.choice(answer)
    response.set_text(message)
    response.set_tts(message + "Доступные команды: {}.".format(" ,".join(user_storage['suggests'])))
    buttons, user_storage = get_suggests(user_storage)
    response.set_buttons(buttons)
    return response, user_storage


def read_answers_data(name):
    import json
    with open(name+".json", encoding="utf-8") as file:
        data = json.loads(file.read())
        return data


aliceAnswers = read_answers_data("data/answers_dict_example")


def check_wrd(wrd):
    import requests
    API_CODE = 'dict.1.1.20190331T101514Z.9cbf4535b1122019.dbd3fb8c0fded55cd45d1f44459bbfda21d8e82a'
    BASIC_REQUEST = '''https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key={API_CODE}&lang=TRANS&text=TEXTWORD'''.format(
        API_CODE=API_CODE)
    ERRORS = {200: 'Запрос выполнен',
              401: 'Ключ API невалиден',
              402: 'Ключ API заблокирован',
              403: 'Превышено суточное ограничение на кол-во запросов',
              413: 'Превышен максимальный размер текста',
              501: 'Заданное направление перевода не поддерживается'}

    url_for_request = BASIC_REQUEST.replace('TRANS', "ru-ru").replace('TEXTWORD', wrd)
    response = requests.get(url_for_request).json()
    if 'code' in response.keys():
        return ERRORS[response['code']]
    else:
        if len(response['def']) > 0:
            return True
        else:
            return False