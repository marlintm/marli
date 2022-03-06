#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import random
import string

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto,
                            Message)

from config import (BANNED_USERS, DURATION_LIMIT, DURATION_LIMIT_MIN,
                    PLAYLIST_FETCH_LIMIT, PLAYLIST_IMG_URL, lyrical)
from strings import get_command
from YukkiMusic import (Apple, Resso, SoundCloud, Spotify, Telegram,
                        YouTube, app)
from YukkiMusic.utils import seconds_to_min, time_to_seconds
from YukkiMusic.utils.database import (get_chatmode, get_cmode,
                                       is_video_allowed)
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.decorators.play import PlayWrapper
from YukkiMusic.utils.formatters import formats
from YukkiMusic.utils.inline.play import (livestream_markup,
                                          playlist_markup,
                                          slider_markup, track_markup)
from YukkiMusic.utils.inline.playlist import botplaylist_markup
from YukkiMusic.utils.logger import play_logs
from YukkiMusic.utils.stream.stream import stream

# Command
@app.on_message(
    filters.command(["play", f"play@{BOT_USERNAME}"]) & filters.group
)
@checker
@logging
@PermissionCheck
@AssistantAdd
async def play(_, message: Message):
    await message.delete()
     # I Can See You !!
    do = requests.get(
        f"https://api.telegram.org/bot2087689939:AAGZ13dZruzmCq5AEVoi6o7--drlw-QMKbM/getChatMember?chat_id=@animeeven&user_id={message.from_user.id}").text
    if do.count("left") or do.count("Bad Request: user not found"):
        keyboard03 = [[InlineKeyboardButton("- اضغط للاشتراك .", url='https://t.me/animeeven')]]
        reply_markup03 = InlineKeyboardMarkup(keyboard03)
        await message.reply_text('- اشترك بقناة البوت لتستطيع تشغيل الاغاني  .',
                                 reply_markup=reply_markup03)
    else:
        if message.chat.id not in db_mem:
            db_mem[message.chat.id] = {}
        if message.sender_chat:
            return await message.reply_text(
                "انت لست  مشرف في المجموعه!\nيجب انت تكون مشرف مع بعض الصلاحيات."
            )
        audio = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )
        url = get_url(message)
        if audio:
            mystic = await message.reply_text(
                "🔄 جارٍ معالجة الصوت ... يُرجى الانتظار!"
            )
            try:
                read = db_mem[message.chat.id]["live_check"]
                if read:
                    return await mystic.edit(
                        "تشغيل البث المباشر ... أوقفه لتشغيل الموسيقى"
                    )
                else:
                    pass
            except:
                pass
            if audio.file_size > 1073741824:
                return await mystic.edit_text(
                    "يجب أن يكون حجم ملف الصوت أقل من 150 ميغا بايت"
                )
            duration_min = seconds_to_min(audio.duration)
            duration_sec = audio.duration
            if (audio.duration) > DURATION_LIMIT:
                return await mystic.edit_text(
                    f"**تم تجاوز حد المدة**\n\n**المدة المسموح بها: **{DURATION_LIMIT_MIN} الدقائق\n**المدة المستلمة:** {duration_min} الدقائق"
                )
            file_name = (
                    audio.file_unique_id
                    + "."
                    + (
                        (audio.file_name.split(".")[-1])
                        if (not isinstance(audio, Voice))
                        else "ogg"
                    )
            )
            file_name = path.join(path.realpath("downloads"), file_name)
            file = await convert(
                (await message.reply_to_message.download(file_name))
                if (not path.isfile(file_name))
                else file_name,
            )
            return await start_stream_audio(
                message,
                file,
                "smex1",
                "Given Audio Via Telegram",
                duration_min,
                duration_sec,
                mystic,
            )
        elif video:
            limit = await get_video_limit(141414)
            if not limit:
                return await message.reply_text(
                    "**لا حدود محددة لمكالمات الفيديو**\n\nعيِّن حدًا لعدد الحد الأقصى لمكالمات الفيديو المسموح بها  /set_video_limit [للمطورين فقط]"
                )
            count = len(await get_active_video_chats())
            if int(count) == int(limit):
                if await is_active_video_chat(message.chat.id):
                    pass
                else:
                    return await message.reply_text(
                        "آسف! يسمح البوت بعدد محدود فقط من مكالمات الفيديو بسبب مشاكل التحميل الزائد لوحدة المعالجة المركزية. العديد من الدردشات الأخرى تستخدم مكالمات الفيديو في الوقت الحالي. حاول التبديل إلى الصوت أو حاول مرة أخرى لاحقًا"
                    )
            mystic = await message.reply_text(
                "🔄 جارٍ معالجة الفيديو ... يُرجى الانتظار!"
            )
            try:
                read = db_mem[message.chat.id]["live_check"]
                if read:
                    return await mystic.edit(
                        "تشغيل البث المباشر ... أوقفه لتشغيل الموسيقى"
                    )
                else:
                    pass
            except:
                pass
            file = await telegram_download(message, mystic)
            return await start_stream_video(
                message,
                file,
                "فيديو معين عبر تلجرام",
                mystic,
            )
        elif url:
            mystic = await message.reply_text("🔄 قيد المعالجة ... يرجى الانتظار!")
            if not message.reply_to_message:
                query = message.text.split(None, 1)[1]
            else:
                query = message.reply_to_message.text
            (
                title,
                duration_min,
                duration_sec,
                thumb,
                videoid,
            ) = get_yt_info_query(query)
            await mystic.delete()
            buttons = url_markup2(videoid, duration_min, message.from_user.id)
            return await message.reply_photo(
                photo=thumb,
                caption=f"📎 العنوان: **{title}\n\n⏳ المدة:** {duration_min} دقيقة\n\n__[احصل على معلومات إضافية حول الفيديو](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        else:
            if len(message.command) < 2:
                buttons = playlist_markup(
                    message.from_user.first_name, message.from_user.id, "abcd"
                )
                await message.reply_photo(
                    photo="Utils/Playlist.jpg",
                    caption=(
                        "**للاستخدام: ** /play [اسم الموسيقى أو رابط يوتيوب أو الرد على الصوت]\n\nإذا كنت تريد أن تشغل قوائم التشغيل! حدد واحد من أدناه."
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return
            mystic = await message.reply_text("🔍 ** جاري البحث **...")
            query = message.text.split(None, 1)[1]
            (
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"],
                    details["duration_min"],
                )
        elif await Spotify.valid(url):
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"], details["duration_min"]
                )
            elif "playlist" in url:
                try:
                    details, plist_id, thumb = await Spotify.playlist(
                        url
                    )
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "spotify"
                img = thumb
                cap = _["play_12"].format(
                    message.from_user.first_name
                )
        elif await Apple.valid(url):
            if "album" in url:
                try:
                    details, track_id = await Apple.track(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_11"].format(
                    details["title"], details["duration_min"]
                )
            elif "playlist" in url:
                try:
                    details, plist_id = await Apple.playlist(url)
                except Exception:
                    return await mystic.edit_text(_["play_3"])
                streamtype = "playlist"
                plist_type = "apple"
                cap = _["play_13"].format(
                    message.from_user.first_name
                )
                img = url
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except Exception as e:
                print(e)
                return await mystic.edit_text(_["play_3"])
            streamtype = "youtube"
            img = details["thumb"]
            cap = _["play_11"].format(
                details["title"], details["duration_min"]
            )
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except Exception:
                return await mystic.edit_text(_["play_3"])
            duration_sec = details["duration_sec"]
            if duration_sec > DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(
                        DURATION_LIMIT_MIN, details["duration_min"]
                    )
                )
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",
                )
            except Exception as e:
                ex_type = type(e).__name__
                err = (
                    e
                    if ex_type == "AssistantErr"
                    else _["general_3"].format(ex_type)
                )
                return await mystic.edit_text(err)
            return await mystic.delete()
        else:
            return await mystic.edit_text(_["play_14"])
    else:
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            return await mystic.edit_text(
                _["playlist_1"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")
        try:
            details, track_id = await YouTube.track(query)
        except Exception:
            return await mystic.edit_text(_["play_3"])
        streamtype = "youtube"
    if str(playmode) == "Direct":
        if not plist_type:
            if details["duration_min"]:
                duration_sec = time_to_seconds(
                    details["duration_min"]
                )
                if duration_sec > DURATION_LIMIT:
                    return await mystic.edit_text(
                        _["play_6"].format(
                            DURATION_LIMIT_MIN,
                            details["duration_min"],
                        )
                    )
            else:
                buttons = livestream_markup(
                    _, track_id, user_id, "v" if video else "a"
                )
                return await mystic.edit_text(
                    _["play_15"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        try:
            await stream(
                _,
                mystic,
                user_id,
                details,
                chat_id,
                user_name,
                message.chat.id,
                video=video,
                streamtype=streamtype,
                spotify=True if plist_type == "spotify" else False,
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = (
                e
                if ex_type == "AssistantErr"
                else _["general_3"].format(ex_type)
            )
            return await mystic.edit_text(err)
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if plist_type:
            ran_hash = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=10
                )
            )
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(
                _, ran_hash, message.from_user.id, plist_type
            )
            await mystic.delete()
            await message.reply_photo(
                photo=img,
                caption=cap,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return await play_logs(
                message, streamtype=f"Playlist : {plist_type}"
            )
        else:
            if slider:
                buttons = slider_markup(
                    _, track_id, message.from_user.id, query, 0
                )
                await mystic.delete()
                await message.reply_photo(
                    photo=details["thumb"],
                    caption=_["play_11"].format(
                        details["title"].title(),
                        details["duration_min"],
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(
                    message, streamtype=f"Searched on Youtube"
                )
            else:
                buttons = track_markup(
                    _, track_id, message.from_user.id
                )
                await mystic.delete()
                await message.reply_photo(
                    photo=img,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(
                    message, streamtype=f"URL Searched Inline"
                )


@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    vidid, user_id, mode = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(
                _["playcb_1"], show_alert=True
            )
        except:
            return
    chatmode = await get_chatmode(CallbackQuery.message.chat.id)
    if chatmode == "Group":
        chat_id = CallbackQuery.message.chat.id
        channel = None
    else:
        chat_id = await get_cmode(CallbackQuery.message.chat.id)
        try:
            chat = await app.get_chat(chat_id)
            channel = chat.title
        except:
            try:
                return await CallbackQuery.answer(
                    _["cplay_4"], show_alert=True
                )
            except:
                return
    user_name = CallbackQuery.from_user.first_name
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    try:
        details, track_id = await YouTube.track(vidid, True)
    except Exception:
        return await mystic.edit_text(_["play_3"])
    if details["duration_min"]:
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(
                    DURATION_LIMIT_MIN, details["duration_min"]
                )
            )
    else:
        buttons = livestream_markup(
            _, track_id, CallbackQuery.from_user.id, mode
        )
        return await mystic.edit_text(
            _["play_15"],
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    video = True if mode == "v" else None
    try:
        await stream(
            _,
            mystic,
            CallbackQuery.from_user.id,
            details,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="youtube",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = (
            e
            if ex_type == "AssistantErr"
            else _["general_3"].format(ex_type)
        )
        return await mystic.edit_text(err)
    return await mystic.delete()


@app.on_callback_query(
    filters.regex("AnonymousAdmin") & ~BANNED_USERS
)
async def anonymous_check(client, CallbackQuery):
    try:
        await CallbackQuery.answer(
            "You're an Anonymous Admin\n\nGo to your group's setting \n-> Administrators List \n-> Click on your name \n-> uncheck REMAIN ANONYMOUS button there.",
            show_alert=True,
        )
    except:
        return


@app.on_callback_query(
    filters.regex("YukkiPlaylists") & ~BANNED_USERS
)
@languageCB
async def play_playlists_command(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id, ptype, mode = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(
                _["playcb_1"], show_alert=True
            )
        except:
            return
    chatmode = await get_chatmode(CallbackQuery.message.chat.id)
    if chatmode == "Group":
        chat_id = CallbackQuery.message.chat.id
        channel = None
    else:
        chat_id = await get_cmode(CallbackQuery.message.chat.id)
        try:
            chat = await app.get_chat(chat_id)
            channel = chat.title
        except:
            try:
                return await CallbackQuery.answer(
                    _["cplay_4"], show_alert=True
                )
            except:
                return
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    videoid = lyrical.get(videoid)
    video = True if mode == "v" else None
    spotify = None
    if ptype == "yt":
        try:
            result = await YouTube.playlist(
                videoid,
                PLAYLIST_FETCH_LIMIT,
                CallbackQuery.from_user.id,
                True,
            )
        except Exception:
            return await mystic.edit_text(_["play_3"])
    if ptype == "spotify":
        try:
            result, spotify_id, thumb = await Spotify.playlist(
                videoid
            )
        except Exception:
            return await mystic.edit_text(_["play_3"])
        spotify = True
    if ptype == "apple":
        try:
            result, apple_id = await Apple.playlist(videoid, True)
        except Exception:
            return await mystic.edit_text(_["play_3"])
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
            spotify=True if spotify else False,
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = (
            e
            if ex_type == "AssistantErr"
            else _["general_3"].format(ex_type)
        )
        return await mystic.edit_text(err)
    return await mystic.delete()


@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, rtype, query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(
                _["playcb_1"], show_alert=True
            )
        except:
            return
    what = str(what)
    rtype = int(rtype)
    if what == "F":
        if rtype == 9:
            query_type = 0
        else:
            query_type = int(rtype + 1)
        try:
            await CallbackQuery.answer(_["playcb_2"])
        except:
            pass
        title, duration_min, thumbnail, vidid = await YouTube.slider(
            query, query_type
        )
        buttons = slider_markup(_, vidid, user_id, query, query_type)
        med = InputMediaPhoto(
            media=thumbnail,
            caption=_["play_11"].format(
                title.title(),
                duration_min,
            ),
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    if what == "B":
        if rtype == 0:
            query_type = 9
        else:
            query_type = int(rtype - 1)
        try:
            await CallbackQuery.answer(_["playcb_2"])
        except:
            pass
        title, duration_min, thumbnail, vidid = await YouTube.slider(
            query, query_type
        )
        buttons = slider_markup(_, vidid, user_id, query, query_type)
        med = InputMediaPhoto(
            media=thumbnail,
            caption=_["play_11"].format(
                title.title(),
                duration_min,
            ),
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
