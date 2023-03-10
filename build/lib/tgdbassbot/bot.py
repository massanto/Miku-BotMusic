import aiogram
import asyncio
import tgdbassbot.config
import tgdbassbot.messages
import json
from tgdbassbot.downloader import SongsDownloader
import tgdbassbot.keyboards

bot = aiogram.Bot(token = tgdbassbot.config.API_TOKEN,
                  parse_mode = aiogram.types.ParseMode.HTML)
loop = asyncio.get_event_loop()
dp = aiogram.Dispatcher(bot, loop = loop)

users = {}


@dp.message_handler(commands = ['start'])
async def start_message(message: aiogram.types.Message):
    if str(message.from_user.id) in users.keys():
        start_message_lang = tgdbassbot.messages.start_messages[users[str(
            message.from_user.id)]['language']]
        await bot.send_message(message.chat.id, start_message_lang)

    elif str(message.from_user.id) not in users.keys():
        keyb = tgdbassbot.keyboards.Keyboards().select_lang()
        await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)
        users[str(message.from_user.id)] = {
            "language": "",
            "show_bitrate": "On",
            "show_hearts": "On",
            "show_audio_format": "On",
            "results_count": "10",
            "favourites_list": [],
            "last_list": "",
            "last_page": "",
            "last_urls_page": "",
            "urls": "",
            "without_formating": "",
            "hearts_buttons": "On",

        }
        update_users_write()


@dp.message_handler(commands = ['song'])
async def search_by_song_title(message: aiogram.types.Message):
    await message.reply(
        tgdbassbot.messages.song_messages[users[str(message.from_user.id)]['language']])


@dp.message_handler(
    lambda message: message.text not in tgdbassbot.config.commands and not message.text.startswith("/newpost"))
async def search_song(message: aiogram.types.Message):
    global number_page_message, you_in_first_page

    song_list, urls_list, without_formating = SongsDownloader(
        f"{message.text}").get_songs_list(int(users[str(message.from_user.id)]['results_count']))
    you_in_first_page = tgdbassbot.messages.you_in_first_page_message[users[str(
        message.from_user.id)]['language']]
    number_page_message = tgdbassbot.messages.number_page_message[users[str(
        message.from_user.id)]['language']]

    if song_list == "NoSongs" and urls_list == "NoSongs":
        await bot.send_message(message.chat.id,
                               tgdbassbot.messages.nothing_messages[users[str(message.from_user.id)]['language']])
    elif not song_list and not urls_list:
        pass
    else:
        users[str(message.from_user.id)
        ]["without_formating"] = without_formating
        # Списки ссылок на песни
        users[str(message.from_user.id)]["urls"] = urls_list
        users[str(message.from_user.id)
        ]["last_list"] = song_list  # Списки песен
        users[str(message.from_user.id)]["last_page"] = 0  # Последняя страница
        # Последний список ссылок на песни
        users[str(message.from_user.id)]["last_urls_page"] = "0"
        list_len = len(users[str(message.from_user.id)]
                       ["last_list"])  # Длинна списка

        keyb = tgdbassbot.keyboards.Keyboards().for_songs_list(urls_list[0],
                                                               message.chat.id,
                                                               int(users[str(message.from_user.id)]["results_count"]))

        await bot.send_message(message.chat.id, number_page_message.format("1",
                                                                           str(list_len)) + '\n'.join(song_list[0]),
                               reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data in ("to_left", "close", "to_right"))
async def change_page(call: aiogram.types.CallbackQuery):
    user_lang = users[str(call.from_user.id)]['language']  # Язык пользователя
    # Последний список песен для пользователя
    user_list_now = users[str(call.from_user.id)]["last_list"]
    # Последний список ссылок на песни
    user_link_list_now = users[str(call.from_user.id)]["urls"]
    # Последняя просмотренная страница
    last_page = users[str(call.from_user.id)]["last_page"]
    if call.data == "to_left":  # Листать влево
        if users[str(call.from_user.id)]["last_page"] == 0:
            await bot.answer_callback_query(call.id,
                                            tgdbassbot.messages.you_in_first_page_message[
                                                user_lang])  # Вы уже на первой странице

        else:
            keyb = tgdbassbot.keyboards.Keyboards().for_songs_list(
                user_link_list_now[users[str(call.from_user.id)]["last_page"] - 1],
                call.message.chat.id, int(users[str(call.from_user.id)]["results_count"]))

            users[str(call.from_user.id)]["last_page"] -= 1
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = tgdbassbot.messages.number_page_message[user_lang].format(
                                            users[str(call.from_user.id)]["last_page"] + 1, len(user_list_now)) +
                                               "\n".join(
                                                   user_list_now[users[str(call.from_user.id)]["last_page"]]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

    elif call.data == "to_right":  # Листать вправо
        if users[str(call.from_user.id)]["last_page"] == len(user_list_now) - 1:
            await bot.answer_callback_query(call.id,
                                            tgdbassbot.messages.nothing_messages[user_lang])  # Ничего не нашлось
        else:
            keyb = tgdbassbot.keyboards.Keyboards().for_songs_list(
                user_link_list_now[users[str(call.from_user.id)]["last_page"] + 1],
                call.message.chat.id, int(users[str(call.from_user.id)]["results_count"]))

            users[str(call.from_user.id)]["last_page"] += 1
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = tgdbassbot.messages.number_page_message[user_lang].format(
                                            users[str(call.from_user.id)]["last_page"] + 1, len(user_list_now)) +
                                               "\n".join(
                                                   user_list_now[users[str(call.from_user.id)]["last_page"]]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)
    elif call.data == "close":
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@dp.callback_query_handler(
    lambda call: call.data.startswith("select") and call.data.split("_")[1] not in ("ru", "en", "es"))
async def select_sound(call: aiogram.types.CallbackQuery):
    get_song_num = call.data.split('_')
    song_num = int(get_song_num[1]) - 1
    page = users[str(call.from_user.id)]["last_page"]
    name = users[str(call.from_user.id)
    ]["without_formating"][page][song_num]["artist"]
    song_name = users[str(call.from_user.id)
    ]["without_formating"][page][song_num]["title"]

    song = SongsDownloader().download_song(
        users[str(call.from_user.id)]["urls"][page][song_num])
    duration = users[str(call.from_user.id)
    ]["without_formating"][page][song_num]["duration"]
    keyb = tgdbassbot.keyboards.Keyboards().like_unlike_keyboard(
        users[str(call.from_user.id)]["hearts_buttons"])
    msg = await bot.send_audio(call.message.chat.id, audio = song, title = f"{name} - {song_name}",
                               performer = song_name,
                               caption = '<a href="https://t.me/dbas_music_bot">🎧DBAS Music</a>', reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data in ["like", "unlike"])
async def like_or_unlike(call: aiogram.types.CallbackQuery):
    user_lang = users[str(call.from_user.id)]['language']

    if call.data == "like":
        users[str(call.from_user.id)]["favourites_list"].append(
            {call.message.audio.title: call.message.audio.file_id})
        update_users_write()
        await bot.answer_callback_query(call.id, tgdbassbot.messages.add_to_favourite[user_lang])
    elif call.data == "unlike":

        for item in users[str(call.from_user.id)]["favourites_list"]:
            for key in item.keys():
                if key == call.message.audio.title:
                    song = users[str(call.from_user.id)
                    ]["favourites_list"].index(item)
                    del users[str(call.from_user.id)]["favourites_list"][song]
        await bot.answer_callback_query(call.id, tgdbassbot.messages.del_from_favourite[user_lang])

        update_users_write()


@dp.callback_query_handler(lambda call: call.data in ["select_ru", "select_en", "select_es"])
async def select_lang(call: aiogram.types.CallbackQuery):
    if call.data == "select_ru":
        users[str(call.from_user.id)]['language'] = "RU"
    if call.data == "select_en":
        users[str(call.from_user.id)]['language'] = "EN"
    if call.data == "select_es":
        users[str(call.from_user.id)]['language'] = "ES"

    update_users_write()
    start_message_lang = tgdbassbot.messages.start_messages[users[str(
        call.from_user.id)]['language']]
    await bot.send_message(call.message.chat.id, start_message_lang)


@dp.message_handler(commands = ['artist'])
async def search_for_artist_name(message: aiogram.types.Message):
    """Искать по артисту"""
    await message.reply(
        tgdbassbot.messages.artist_messages[users[str(message.from_user.id)]['language']])


@dp.message_handler(commands = ['setlang'])
async def change_language(message: aiogram.types.Message):
    """Изменить язык"""
    keyb = tgdbassbot.keyboards.Keyboards().select_lang()

    await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)


@dp.message_handler(commands = ['settings'])
async def change_settings(message: aiogram.types.Message):
    """Меню настроек"""

    setting_keyb = tgdbassbot.keyboards.Keyboards().settings(users[str(message.from_user.id)]['language'],
                                                             users[str(message.from_user.id)
                                                             ]['results_count'],
                                                             users[str(message.from_user.id)]['hearts_buttons'])

    await bot.send_message(message.chat.id,
                           tgdbassbot.messages.settings_menu[users[str(message.from_user.id)]['language']],
                           reply_markup = setting_keyb)


@dp.message_handler(commands = ['my'])
async def user_playlist(message: aiogram.types.Message):
    user_lang = users[str(message.from_user.id)]['language']
    playlist = users[str(message.from_user.id)]['favourites_list']
    users[str(message.from_user.id)]["playlist_page"] = 0

    if not playlist:
        await bot.send_message(message.chat.id, tgdbassbot.messages.no_playlist[user_lang])

    else:
        users[str(message.from_user.id)]["playlist_page"] = 0
        f = lambda A, n=int(users[str(message.from_user.id)]['results_count']): [
            A[i:i + n] for i in range(0, len(A), n)]
        cut_playlist = f(playlist)

        keyb = tgdbassbot.keyboards.Keyboards().for_user_playlist(
            cut_playlist[users[str(message.from_user.id)]["playlist_page"]],
            message.chat.id, int(users[str(message.from_user.id)]["results_count"]))
        user_playlist = []
        i = 1
        for item in cut_playlist[0]:
            for key, val in item.items():
                user_playlist.append(f"{i}. {key}")
                i += 1

        await bot.send_message(message.chat.id, '\n'.join(user_playlist), reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data == "to_right_playlist")
async def to_right_user_playlisy(call: aiogram.types.CallbackQuery):
    playlist = users[str(call.from_user.id)]['favourites_list']
    playlist_page = users[str(call.from_user.id)]["playlist_page"]
    user_lang = users[str(call.from_user.id)]['language']
    try:

        if len(playlist) > 1 and playlist_page != len(playlist) - 1:
            users[str(call.from_user.id)]["playlist_page"] += 1
            f = lambda A, n=int(users[str(call.from_user.id)]['results_count']): [
                A[i:i + n] for i in range(0, len(A), n)]
            cut_playlist = f(playlist)
            keyb = tgdbassbot.keyboards.Keyboards().for_user_playlist(
                playlist[users[str(call.from_user.id)]["playlist_page"]],
                call.message.chat.id, int(users[str(call.from_user.id)]["results_count"]))
            user_playlist = []
            i = 1

            for item in cut_playlist[users[str(call.from_user.id)]["playlist_page"]]:
                for key, val in item.items():
                    user_playlist.append(f"{i}. {key}")
                    i += 1

            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = '\n'.join(user_playlist),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

        else:
            await bot.answer_callback_query(call.id, tgdbassbot.messages.nothing_messages[user_lang])

    except IndexError:
        await bot.answer_callback_query(call.id, tgdbassbot.messages.nothing_messages[user_lang])


@dp.callback_query_handler(lambda call: call.data in ["change_lang", "count_result", "heart_buttons"])
async def settings_menu_changer(call: aiogram.types.CallbackQuery):
    if call.data == "change_lang":
        keyb = tgdbassbot.keyboards.Keyboards().select_lang()
        await bot.send_message(call.message.chat.id, "Выбери язык\nChoose a language\nElige un idioma",
                               reply_markup = keyb)
    elif call.data == "count_result":
        if users[str(call.from_user.id)]["results_count"] == "10":
            users[str(call.from_user.id)]["results_count"] = "6"
        elif users[str(call.from_user.id)]["results_count"] == "6":
            users[str(call.from_user.id)]["results_count"] = "8"
        elif users[str(call.from_user.id)]["results_count"] == "8":
            users[str(call.from_user.id)]["results_count"] = "10"

        setting_keyb = tgdbassbot.keyboards.Keyboards().settings(users[str(call.from_user.id)]['language'],
                                                                 users[str(call.from_user.id)
                                                                 ]['results_count'],
                                                                 users[str(call.from_user.id)]['hearts_buttons'])
        update_users_write()
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text = tgdbassbot.messages.settings_menu[users[str(
                                        call.from_user.id)]['language']],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)
    elif call.data == "heart_buttons":
        if users[str(call.from_user.id)]["hearts_buttons"] == "On":
            users[str(call.from_user.id)]["hearts_buttons"] = "Off"
        elif users[str(call.from_user.id)]["hearts_buttons"] == "Off":
            users[str(call.from_user.id)]["hearts_buttons"] = "On"

        setting_keyb = tgdbassbot.keyboards.Keyboards().settings(users[str(call.from_user.id)]['language'],
                                                                 users[str(call.from_user.id)
                                                                 ]['results_count'],
                                                                 users[str(call.from_user.id)]['hearts_buttons'])

        update_users_write()
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text = tgdbassbot.messages.settings_menu[users[str(
                                        call.from_user.id)]['language']],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)


@dp.message_handler(commands = ['newpost'])
async def malling(message: aiogram.types.Message):
    text_for_malling = message.text.replace('/newpost', '')
    update_users_read()

    i = 0
    for item in users.keys():
        try:
            await bot.send_message(int(item), text_for_malling)
            i += 1
        except (aiogram.exceptions.BotBlocked, aiogram.exceptions.ChatNotFound):
            pass

    await bot.send_message(message.chat.id, f'Сообщение получили <b>{i}</b> пользователей')


@dp.message_handler(commands = ['users'])
async def howusers(message: aiogram.types.Message):
    update_users_read()
    await bot.send_message(message.chat.id, f"<em>Кол-во пользователей</em>\n\n<b>{len(users)}</b> пользователей")


@dp.callback_query_handler(lambda call: call.data.startswith("playlist"))
async def select_sound(call: aiogram.types.CallbackQuery):
    get_song_num = call.data.split('_')
    playlist = users[str(call.from_user.id)]['favourites_list']
    song_num = int(get_song_num[1]) - 1
    page = users[str(call.from_user.id)]["playlist_page"]

    f = lambda A, n=int(users[str(call.from_user.id)]['results_count']): [
        A[i:i + n] for i in range(0, len(A), n)]
    cut_playlist = f(playlist)
    keyb = tgdbassbot.keyboards.Keyboards().like_unlike_keyboard(
        users[str(call.from_user.id)]["hearts_buttons"])
    for val in cut_playlist[page][song_num].values():
        await bot.send_audio(call.message.chat.id, audio = val,
                             caption = '<a href="https://t.me/dbas_music_bot">🎧DBAS Music</a>', reply_markup = keyb)


def update_users_write():
    with open('./data/users.json', 'w', encoding = 'UTF-8') as write_users:
        json.dump(users, write_users, ensure_ascii = False, indent = 4)





def update_users_read():
    global users
    with open("./data/users.json", 'r', encoding = 'UTF-8') as read_users:
        users = json.load(read_users)


if __name__ == "__main__":
    update_users_read()
    aiogram.executor.start_polling(dp, skip_updates = True)
