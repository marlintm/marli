from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden

@Client.on_message(~filters.edited & filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    if not MUST_JOIN:  
        return
    try:
        try:
            await bot.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await bot.get_chat(MUST_JOIN)
                link = chat_info.invite_link
            try:
                await msg.reply(
                    f"🚸 | عـلـيك الاشـتراك فـي\n\n 🎯 | قـناة : [سـورس مـيوزك .](https://t.me/MusicElkeatib)\n\n 🚀 | لـتتمـكن مـن استـخـدامـي\n\n ✅ | بعد الاشـتراك أرسل (« /start »)   -《 🇾🇪 》-",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("ᵐ༒︎𝙕𝙊𝙍𝙊_𝙈𝙐𝙎𝙄𝘾♲︎︎༒︎ᵏ︎", url="https://t.me/MusicElkeatib")]
                    ])
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"انا لست ادمن في المجموعة MUST_JOIN  : {MUST_JOIN} !")

