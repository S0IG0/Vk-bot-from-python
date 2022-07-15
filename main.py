from coronovirus import parse_russia, parse_coronavirus
from weather_links import parse_weather_now, parse_weather_day, parse_weather_day_tomorrow, parse_weather_day_5_days
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import token, WEEK, PARITY_WEEK, REVERSE_WEEK
from test import check_in_keys, create_image, get_current_week, get_teacher_list, check_in_keys_teachers, \
    create_image_teachers
import string
import datetime
import pickle

FORBIDDEN = string.punctuation


def main():
    vk_session = vk_api.VkApi(token=token)
    upload = VkUpload(vk_session)
    vk = vk_session.get_api()

    #################################################################
    with open(r'data/pickle/users/users.pickle', 'rb') as file:  #
        users = pickle.load(file)  #
    #################################################################

    start_keyboard = VkKeyboard(one_time=True)
    start_keyboard.add_button('Расписание', color=VkKeyboardColor.SECONDARY)
    start_keyboard.add_button('Погода', color=VkKeyboardColor.SECONDARY)
    start_keyboard.add_button('Коронавирус', color=VkKeyboardColor.SECONDARY)

    schedule_keyboard = VkKeyboard(one_time=True)
    schedule_keyboard.add_button('На сегодня', color=VkKeyboardColor.POSITIVE)
    schedule_keyboard.add_button('На завтра', color=VkKeyboardColor.NEGATIVE)
    schedule_keyboard.add_line()
    schedule_keyboard.add_button('На эту неделю', color=VkKeyboardColor.PRIMARY)
    schedule_keyboard.add_button('На следующую неделю', color=VkKeyboardColor.PRIMARY)
    schedule_keyboard.add_line()
    schedule_keyboard.add_button('Какая неделя?', color=VkKeyboardColor.SECONDARY)
    schedule_keyboard.add_button('Какая группа?', color=VkKeyboardColor.SECONDARY)
    schedule_keyboard.add_line()
    schedule_keyboard.add_button('Поменять группу', color=VkKeyboardColor.NEGATIVE)

    teacher_keyboard = VkKeyboard(one_time=True)
    teacher_keyboard.add_button('На сегодня', color=VkKeyboardColor.POSITIVE)
    teacher_keyboard.add_button('На завтра', color=VkKeyboardColor.NEGATIVE)
    teacher_keyboard.add_line()
    teacher_keyboard.add_button('На эту неделю', color=VkKeyboardColor.PRIMARY)
    teacher_keyboard.add_button('На следующую неделю', color=VkKeyboardColor.PRIMARY)

    weather_keyboard = VkKeyboard(one_time=True)
    weather_keyboard.add_button('Сейчас', color=VkKeyboardColor.POSITIVE)
    weather_keyboard.add_button('Сегодня', color=VkKeyboardColor.NEGATIVE)
    weather_keyboard.add_button('Завтра', color=VkKeyboardColor.NEGATIVE)
    weather_keyboard.add_line()
    weather_keyboard.add_button('На 5 дней', color=VkKeyboardColor.PRIMARY)

    read_group = False
    current_search = ''
    teacher_name = ''

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.text and event.to_me:

            #################################################################
            with open(r'data/pickle/users/users.pickle', 'wb') as file:  #
                pickle.dump(users, file)  #
            #################################################################

            try:
                text_output = ''
                keyboard = None
                attachment = ''

                text_ = event.text
                text = event.text.translate(
                    str.maketrans('', '', string.punctuation.replace('-', '') + string.ascii_letters)
                ).lower().strip()

                if text == 'привет':
                    text_output = 'Привет, ' + vk.users.get(user_id=event.user_id)[0]['first_name']

                elif text == 'бот':
                    text_output = "Показать расписание"
                    keyboard = schedule_keyboard

                elif check_in_keys_teachers(text_):
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=f'Выбери нужный пункт :D',
                        keyboard=teacher_keyboard.get_keyboard(),
                    )
                    teacher_name = text_
                    continue

                elif text.split()[0] == 'бот' and check_in_keys(text.split()[1].upper()):
                    name_group = text.split()[1].upper()
                    text_output = f"Показать расписание, для: {name_group}"
                    keyboard = schedule_keyboard

                    current_search = name_group

                elif text.split()[0] == 'бот' \
                        and text.split()[1].upper() in list(WEEK.values())[:-1] \
                        and check_in_keys(text.split()[2].upper()):

                    name_group_ = text.split()[2].upper()
                    name_week_ = text.split()[1].upper()

                    attachments = []

                    create_image(name_group_, PARITY_WEEK[get_current_week() % 2], name_week_)
                    photo = upload.photo_messages(photos=rf'data/image_data/{name_week_}.png', peer_id=event.peer_id)
                    attachments.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')

                    create_image(name_group_, PARITY_WEEK[(get_current_week() + 1) % 2], name_week_)
                    photo = upload.photo_messages(photos=rf'data/image_data/{name_week_}.png', peer_id=event.peer_id)
                    attachments.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')
                    keyboard = start_keyboard

                    for item, temp in zip(attachments, [get_current_week() % 2, (get_current_week() + 1) % 2]):
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message=f'Расписание на {name_week_}, {temp + 1} неделя',
                            keyboard=keyboard.get_keyboard(),
                            attachment=item
                        )
                    continue

                elif text.split()[0] == 'найти':
                    teachers = get_teacher_list(text.split()[1])
                    if not teachers:
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message=f'Я не могу найти: {text.split()[1]}',
                        )
                        continue
                    else:
                        temp_keyboard = VkKeyboard(one_time=True)
                        temp_keyboard.add_button(teachers[0], color=VkKeyboardColor.SECONDARY)

                        for name in teachers[1:]:
                            temp_keyboard.add_line()
                            temp_keyboard.add_button(name, color=VkKeyboardColor.SECONDARY)

                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message=f'Выбери нужного преподавателя',
                            keyboard=temp_keyboard.get_keyboard(),
                        )
                        continue

                elif text.split()[0] == 'сейчас':

                    if len(text.split()) != 1:
                        text_output, path = parse_weather_now(text.split()[1])
                        if text_output == 'Город не найден':
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message='Я не знаю такого города.',
                                keyboard=start_keyboard.get_keyboard(),
                            )
                            continue

                    else:
                        text_output, path = parse_weather_now()

                    photo = upload.photo_messages(photos=path, peer_id=event.peer_id)
                    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        attachment=attachment,
                    )

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=start_keyboard.get_keyboard(),
                    )
                    continue

                elif text.split()[0] == 'сегодня':

                    if len(text.split()) != 1:
                        text_output, path = parse_weather_day(text.split()[1])
                        if text_output == 'Город не найден':
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message='Я не знаю такого города.',
                                keyboard=start_keyboard.get_keyboard(),
                            )
                            continue

                    else:
                        text_output, path = parse_weather_day()

                    photo = upload.photo_messages(photos=path, peer_id=event.peer_id)
                    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        attachment=attachment,
                    )

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=start_keyboard.get_keyboard(),
                    )
                    continue
                elif text.split()[0] == 'завтра':

                    if len(text.split()) != 1:
                        text_output, path = parse_weather_day_tomorrow(text.split()[1])
                        if text_output == 'Город не найден':
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message='Я не знаю такого города.',
                                keyboard=start_keyboard.get_keyboard(),
                            )
                            continue

                    else:
                        text_output, path = parse_weather_day_tomorrow()

                    photo = upload.photo_messages(photos=path, peer_id=event.peer_id)
                    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        attachment=attachment,
                    )

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=start_keyboard.get_keyboard(),
                    )
                    continue

                elif text.split()[:3] == ['на', '5', 'дней']:
                    if len(text.split()) > 3:
                        text_output, path = parse_weather_day_5_days(text.split()[3])
                        if text_output == 'Город не найден':
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message='Я не знаю такого города.',
                                keyboard=start_keyboard.get_keyboard(),
                            )
                            continue

                    else:
                        text_output, path = parse_weather_day_5_days()

                    photo = upload.photo_messages(photos=path, peer_id=event.peer_id)
                    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        attachment=attachment,
                    )

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=start_keyboard.get_keyboard(),
                    )
                    continue

                elif text.split()[0] == 'коронавирус':

                    if len(text.split()) != 1:
                        text_output, path = parse_coronavirus(text.split()[1])  # parse_russia(text.split()[1])
                        if text_output == 'Город не найден':
                            vk.messages.send(
                                user_id=event.user_id,
                                random_id=get_random_id(),
                                message='Я не знаю такого города.',
                                keyboard=start_keyboard.get_keyboard(),
                            )
                            continue

                    else:
                        text_output, path = parse_russia()

                    photo = upload.photo_messages(photos=path, peer_id=event.peer_id)
                    attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'

                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=start_keyboard.get_keyboard(),
                    )
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        attachment=attachment,
                    )
                    continue

                elif text == 'погода':
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message='Выбери нужный пункт',
                        keyboard=weather_keyboard.get_keyboard(),
                    )
                    continue

                elif text == 'какая группа':
                    text_output = f'Показываю расписание группы {users[event.user_id]}'
                    keyboard = start_keyboard

                elif check_in_keys(text.upper()):
                    users[event.user_id] = text.upper()
                    text_output = f'Я запомнил, что ты из группы {users[event.user_id]}.'
                    keyboard = start_keyboard

                elif text == 'начать':
                    text_output = f'Привет, {vk.users.get(user_id=event.user_id)[0]["first_name"]}.\n' \
                                  f'Я бот помощник. Я умею показывать расписание' \
                                  f' для студентов ИТ и погоду на сегодня.\n' \
                                  f'Чтобы узнать расписание, напиши расписание.\n' \
                                  f'Чтобы узнать погоду, напиши погода.\n' \
                                  f'Или нажми на нужную кнопку\n' + """команды:
__1. Привет
__2. Бот
__3. Бот “номер группы”
__4. Бот “день недели” “номер группы”
__5. Найти
__6. Сейчас
__7. Сейчас “Город/страна/регион”
__8. Сегодня
__9. Сегодня “Город/страна/регион”
__10. Завтра
__11. Завтра “Город/страна/регион”
__12. На 5 дней
__13. На 5 дней “Город/страна/регион”
__14. Коронавирус
__15. Коронавирус “Город/страна/регион”
__16. Погода
__17. Какая группа?
__18. “номер группы”
__19. Начать
__20. Расписание
__21. На сегодня
__22. На завтра
__23. На эту неделю
__24. На следующую неделю
__25. Какая неделя
__26. Поменять группу
__27. “День недели”
"""
                    keyboard = start_keyboard

                elif text == 'расписание':
                    if not (event.user_id in users.keys()):
                        text_output = f'{vk.users.get(user_id=event.user_id)[0]["first_name"]}, ' \
                                      f'я вижу ты первый раз спрашиваешь у меня расписание ' \
                                      f'напиши пожалуйста свою группу в чат.'
                        read_group = True
                        keyboard = start_keyboard
                    else:
                        text_output = 'Выбери нужный пункт ;)'
                        keyboard = schedule_keyboard

                elif text == 'на сегодня':
                    name_week = WEEK[datetime.datetime.today().weekday() + 1]
                    time = datetime.datetime.today()
                    if name_week == WEEK[len(WEEK)]:
                        name_week = WEEK[1]
                        time = (datetime.date.today() + datetime.timedelta(days=1))

                    if teacher_name == '':
                        if current_search != '':
                            create_image(current_search, PARITY_WEEK[get_current_week() % 2], name_week)
                            current_search = ''
                        else:
                            create_image(users[event.user_id], PARITY_WEEK[get_current_week() % 2], name_week)

                        text_output = f'Расписание на {time}, {name_week.lower()}'
                        photo = upload.photo_messages(photos=rf'data/image_data/{name_week}.png', peer_id=event.peer_id)
                        attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
                        keyboard = start_keyboard
                    else:
                        create_image_teachers(teacher_name, PARITY_WEEK[get_current_week() % 2], name_week)
                        text_output = f'Расписание на {time} для: {teacher_name}, {name_week.lower()}'
                        teacher_name = ''
                        photo = upload.photo_messages(photos=rf'data/image_data/teachers/{name_week}.png',
                                                      peer_id=event.peer_id)
                        attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
                        keyboard = start_keyboard

                elif text == 'на завтра':
                    name_week = WEEK[datetime.datetime.today().weekday() + 1]
                    time = datetime.datetime.today()
                    if name_week == WEEK[len(WEEK) - 1]:
                        name_week = WEEK[1]
                        time = (datetime.date.today() + datetime.timedelta(days=3))
                    elif name_week == WEEK[len(WEEK)]:
                        name_week = WEEK[2]
                        time = (datetime.date.today() + datetime.timedelta(days=2))
                    else:
                        name_week = WEEK[(datetime.date.today() + datetime.timedelta(days=1)).weekday() + 1]
                        time = (datetime.date.today() + datetime.timedelta(days=1))

                    if teacher_name == '':
                        if current_search != '':
                            create_image(current_search, PARITY_WEEK[get_current_week() % 2], name_week)
                            current_search = ''
                        else:
                            create_image(users[event.user_id], PARITY_WEEK[get_current_week() % 2], name_week)

                        text_output = f'Расписание на {time}, {name_week.lower()}'
                        photo = upload.photo_messages(photos=rf'data/image_data/{name_week}.png', peer_id=event.peer_id)
                        attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
                        keyboard = start_keyboard
                    else:
                        create_image_teachers(teacher_name, PARITY_WEEK[get_current_week() % 2], name_week)
                        text_output = f'Расписание на {time} для: {teacher_name}, {name_week.lower()}'
                        teacher_name = ''
                        photo = upload.photo_messages(photos=rf'data/image_data/teachers/{name_week}.png',
                                                      peer_id=event.peer_id)
                        attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
                        keyboard = start_keyboard

                elif text == 'на эту неделю':
                    if teacher_name == '':
                        if current_search != '':
                            create_image(current_search, PARITY_WEEK[get_current_week() % 2])
                            current_search = ''
                        else:
                            create_image(users[event.user_id], PARITY_WEEK[get_current_week() % 2])

                        text_output = f'Расписание на эту неделю'
                        attachment = []
                        for value in list(WEEK.values())[:-1]:
                            photo = upload.photo_messages(photos=fr'data/image_data/{value}.png', peer_id=event.peer_id)
                            attachment.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')
                        keyboard = start_keyboard
                    else:
                        create_image_teachers(teacher_name, PARITY_WEEK[get_current_week() % 2])
                        text_output = f'Расписание на эту неделю, для: {teacher_name}'
                        teacher_name = ''
                        attachment = []
                        for value in list(WEEK.values())[:-1]:
                            photo = upload.photo_messages(photos=fr'data/image_data/teachers/{value}.png',
                                                          peer_id=event.peer_id)
                            attachment.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')
                        keyboard = start_keyboard

                elif text == 'на следующую неделю':

                    if teacher_name == '':
                        if current_search != '':
                            create_image(current_search, PARITY_WEEK[(get_current_week() + 1) % 2])
                            current_search = ''
                        else:
                            create_image(users[event.user_id], PARITY_WEEK[(get_current_week() + 1) % 2])

                        text_output = f'Расписание на следующую неделю'
                        attachment = []
                        for value in list(WEEK.values())[:-1]:
                            photo = upload.photo_messages(photos=fr'data/image_data/{value}.png', peer_id=event.peer_id)
                            attachment.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')
                        keyboard = start_keyboard
                    else:
                        create_image_teachers(teacher_name, PARITY_WEEK[(get_current_week() + 1) % 2])
                        text_output = f'Расписание на следующую неделю, для: {teacher_name}'
                        teacher_name = ''
                        attachment = []
                        for value in list(WEEK.values())[:-1]:
                            photo = upload.photo_messages(photos=fr'data/image_data/teachers/{value}.png',
                                                          peer_id=event.peer_id)
                            attachment.append(f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}')
                        keyboard = start_keyboard

                elif text == 'какая неделя':
                    text_output = f'Сегодня уже: {get_current_week()} неделя.'
                    keyboard = start_keyboard
                elif text == 'поменять группу':
                    text_output = 'Введи пожалуйста номер своей группы.'
                    read_group = True
                elif text.upper() in WEEK.values():
                    keyboard = start_keyboard
                    if text.upper() == WEEK[len(WEEK)]:
                        text_output = f"Дорогой студент, в воскресенье ты отдыхаешь :З"
                    else:
                        if REVERSE_WEEK[text.upper()] <= REVERSE_WEEK[WEEK[datetime.datetime.today().weekday() + 1]]:
                            create_image(users[event.user_id], PARITY_WEEK[get_current_week() % 2], text.upper())
                        else:
                            create_image(users[event.user_id], PARITY_WEEK[(get_current_week() + 1) % 2], text.upper())
                        photo = upload.photo_messages(
                            photos=rf'data/image_data/{text.upper()}.png',
                            peer_id=event.peer_id
                        )
                        attachment = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}_{photo[0]["access_key"]}'
                        text_output = f'Расписание на {text}'

                elif read_group:
                    if check_in_keys(text.upper()):
                        text_output = f'Спасибо, твой номер группы я запомнил.\n' \
                                      f'В следующий достаточно написать: расписание'
                        users[event.user_id] = text.upper()
                        read_group = False
                    else:
                        text_output = f'Я не знаю такой группы, попробуй еще раз ' \
                                      f'написать или выбрать пункт расписание ' \
                                      f'и ввести номер группы заново.'
                    keyboard = start_keyboard

                if text in ['привет', 'поменять группу']:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output
                    )
                elif text in ['на сегодня', 'на завтра'] or text.upper() in list(WEEK.values())[:-1]:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=keyboard.get_keyboard(),
                        attachment=attachment
                    )
                elif text in ['на эту неделю', 'на следующую неделю']:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                    )
                    for item, name_week in zip(attachment, list(WEEK.values())[:-1]):
                        vk.messages.send(
                            user_id=event.user_id,
                            random_id=get_random_id(),
                            message=name_week,
                            keyboard=keyboard.get_keyboard(),
                            attachment=item
                        )
                elif text in ['расписание', 'начать', 'какая группа', 'какая неделя', 'бот'] \
                        or text.split()[0] == 'бот' and check_in_keys(text.split()[1].upper()) \
                        or check_in_keys(text.upper()) \
                        or text.upper() == WEEK[len(WEEK)] \
                        or read_group or not read_group:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=text_output,
                        keyboard=keyboard.get_keyboard()
                    )
                else:
                    vk.messages.send(
                        user_id=event.user_id,
                        random_id=get_random_id(),
                        message=f"Я не знаю такой команды, что бы узнать, что я умею напиши: начать.",
                    )
            except BaseException as exc:
                print(exc)
                vk.messages.send(
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=f"Ты что-то делаешь не так, чтобы узнать как мною пользоваться напиши: начать",
                )


if __name__ == '__main__':
    main()
