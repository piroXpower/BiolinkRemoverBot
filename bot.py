import os
import re
import sys
import git
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions
)
from pyrogram.enums import ChatMemberStatus

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SUPPORT_CHAT
from database import get_chat_settings, update_chat_settings

app = Client(
    name="biolink_protector",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

URL_PATTERN = re.compile(
    r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"https?://[a-zA-Z0-9]+\.[^\s]{2,}|"
    r"t\.me/[a-zA-Z0-9_]+|"
    r"[a-zA-Z0-9-]+\.(?:com|org|net|io|me|info|xyz|top|live|ru|in|co|site|biz|link|online|app))",
    re.IGNORECASE
)

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# --- Commands ---

@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    text = (
        "✨ **Welcome to BioLink Protector Bot!** ✨\n\n"
        "🛡️ I help protect your groups from users with links in their bio.\n\n"
        "🔹 **Key Features:**\n"
        "   • Automatic URL detection in user bios\n"
        "   • Customizable warning limit\n"
        "   • Auto-mute or ban when limit is reached\n"
        "   • Whitelist management for trusted users\n\n"
        "Use /help to see all available commands."
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT),
            InlineKeyboardButton("📢 Support Channel", url=SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton("➕ Add Me to Your Group", url=f"https://t.me/{(await app.get_me()).username}?startgroup=true")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, disable_web_page_preview=True)
@app.on_message(filters.command("help"))
async def help_handler(_, message: Message):
    text = (
        "🛠️ **Bot Commands & Usage**\n\n"
        "`/config` – set warn-limit & punishment mode\n"
        "`/free` – whitelist a user (reply or user/id)\n"
        "`/unfree` – remove from whitelist\n"
        "`/freelist` – list all whitelisted users\n"
        "`/update` – update bot from GitHub (Owner only)\n\n"
        "**When someone with a URL in their bio posts, I’ll:**\n"
        " 1. ⚠️ Warn them\n"
        " 2. 🔇 Mute if they exceed limit\n"
        " 3. 🔨 Ban if set to ban\n\n"
        "Use the inline buttons on warnings to cancel or whitelist."
    )
    await message.reply_text(text)

@app.on_message(filters.command("config") & filters.group)
async def config_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only group admins can use this command.")

    settings = get_chat_settings(message.chat.id)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Mode: {settings['action'].upper()}", callback_data="toggle_action"),
        ],
        [
            InlineKeyboardButton(f"Limit: {settings['warn_limit']}", callback_data="change_limit")
        ]
    ])
    await message.reply_text(
        f"⚙️ **Configuration for {message.chat.title}**\n\n"
        f"• **Current Action:** `{settings['action']}`\n"
        f"• **Warn Limit:** `{settings['warn_limit']}`",
        reply_markup=buttons
    )

@app.on_message(filters.command("free") & filters.group)
async def free_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only group admins can whitelist members.")

    target_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
        except ValueError:
            user = await app.get_users(message.command[1])
            target_id = user.id

    if not target_id:
        return await message.reply_text("⚠️ Reply to a user or pass their username/user ID.")

    settings = get_chat_settings(message.chat.id)
    if target_id not in settings["whitelist"]:
        settings["whitelist"].append(target_id)
        settings["warns"].pop(str(target_id), None)
        update_chat_settings(message.chat.id, "whitelist", settings["whitelist"])
        update_chat_settings(message.chat.id, "warns", settings["warns"])
        await message.reply_text(f"✅ User `{target_id}` added to whitelist.")
    else:
        await message.reply_text("ℹ️ User is already whitelisted.")

@app.on_message(filters.command("unfree") & filters.group)
async def unfree_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only group admins can modify the whitelist.")

    target_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
        except ValueError:
            user = await app.get_users(message.command[1])
            target_id = user.id

    if not target_id:
        return await message.reply_text("⚠️ Reply to a user or pass their username/user ID.")

    settings = get_chat_settings(message.chat.id)
    if target_id in settings["whitelist"]:
        settings["whitelist"].remove(target_id)
        update_chat_settings(message.chat.id, "whitelist", settings["whitelist"])
        await message.reply_text(f"🗑️ User `{target_id}` removed from whitelist.")
    else:
        await message.reply_text("ℹ️ User was not found in the whitelist.")

@app.on_message(filters.command("freelist") & filters.group)
async def freelist_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ Only group admins can view the whitelist.")

    settings = get_chat_settings(message.chat.id)
    whitelist = settings.get("whitelist", [])
    if not whitelist:
        return await message.reply_text("📋 Whitelist is currently empty.")

    out = "📋 **Whitelisted Users:**\n\n"
    for uid in whitelist:
        out += f"• `{uid}`\n"
    await message.reply_text(out)

@app.on_message(filters.command("update") & filters.user(OWNER_ID))
async def update_handler(_, message: Message):
    status_msg = await message.reply_text("🔄 Checking for Git updates...")
    try:
        repo = git.Repo(".")
        origin = repo.remotes.origin
        pull = origin.pull()
        
        if "Already up to date." in str(pull):
            return await status_msg.edit_text("✅ Bot is already running the latest commit.")
        
        await status_msg.edit_text("🚀 Pulled latest changes! Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await status_msg.edit_text(f"❌ Update failed: `{e}`")

# --- Bio Inspector ---

@app.on_message(filters.group & ~filters.bot)
async def bio_scanner(_, message: Message):
    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    settings = get_chat_settings(chat_id)

    if user.id in settings["whitelist"] or await is_admin(chat_id, user.id):
        return

    try:
        user_info = await app.get_chat(user.id)
        bio = user_info.bio or ""
    except Exception:
        return

    if URL_PATTERN.search(bio):
        uid_str = str(user.id)
        current_warns = settings["warns"].get(uid_str, 0) + 1
        settings["warns"][uid_str] = current_warns
        update_chat_settings(chat_id, "warns", settings["warns"])

        if current_warns >= settings["warn_limit"]:
            settings["warns"].pop(uid_str, None)
            update_chat_settings(chat_id, "warns", settings["warns"])

            if settings["action"] == "ban":
                await app.ban_chat_member(chat_id, user.id)
                await message.reply_text(f"🔨 {user.mention} has been **banned** for bio links exceeding the warn limit.")
            else:
                await app.restrict_chat_member(
                    chat_id,
                    user.id,
                    ChatPermissions(can_send_messages=False)
                )
                await message.reply_text(f"🔇 {user.mention} has been **muted** for bio links exceeding the warn limit.")
            return

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("❌ Reset Warn", callback_data=f"reset_{user.id}"),
                InlineKeyboardButton("🛡️ Whitelist", callback_data=f"wl_{user.id}")
            ]
        ])

        await message.reply_text(
            f"⚠️ {user.mention}, **links in bio are not allowed! Please Remove it to chat**\n"
            f"• Warning: **{current_warns}/{settings['warn_limit']}**\n"
            f"• Action upon limit: **{settings['action'].upper()}**",
            reply_markup=buttons
        )

# --- Callbacks ---

@app.on_callback_query()
async def callback_dispatcher(_, query: CallbackQuery):
    chat_id = query.message.chat.id
    admin_id = query.from_user.id

    if not await is_admin(chat_id, admin_id):
        return await query.answer("❌ Only administrators can perform this action.", show_alert=True)

    settings = get_chat_settings(chat_id)
    data = query.data

    if data == "toggle_action":
        new_action = "ban" if settings["action"] == "mute" else "mute"
        update_chat_settings(chat_id, "action", new_action)
        settings["action"] = new_action
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"Mode: {settings['action'].upper()}", callback_data="toggle_action"),
            ],
            [
                InlineKeyboardButton(f"Limit: {settings['warn_limit']}", callback_data="change_limit")
            ]
        ])
        await query.message.edit_reply_markup(reply_markup=btn)
        await query.answer(f"Action switched to {new_action.upper()}")

    elif data == "change_limit":
        limits = [1, 2, 3, 5]
        curr_idx = limits.index(settings["warn_limit"]) if settings["warn_limit"] in limits else 0
        new_limit = limits[(curr_idx + 1) % len(limits)]
        update_chat_settings(chat_id, "warn_limit", new_limit)
        settings["warn_limit"] = new_limit
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"Mode: {settings['action'].upper()}", callback_data="toggle_action"),
            ],
            [
                InlineKeyboardButton(f"Limit: {settings['warn_limit']}", callback_data="change_limit")
            ]
        ])
        await query.message.edit_reply_markup(reply_markup=btn)
        await query.answer(f"Warn limit set to {new_limit}")

    elif data.startswith("reset_"):
        target_uid = data.split("_")[1]
        settings["warns"].pop(target_uid, None)
        update_chat_settings(chat_id, "warns", settings["warns"])
        await query.message.edit_text(f"✅ Warning reset for user `{target_uid}` by {query.from_user.mention}.")
        await query.answer("Warn reset.")

    elif data.startswith("wl_"):
        target_uid = int(data.split("_")[1])
        if target_uid not in settings["whitelist"]:
            settings["whitelist"].append(target_uid)
            settings["warns"].pop(str(target_uid), None)
            update_chat_settings(chat_id, "whitelist", settings["whitelist"])
            update_chat_settings(chat_id, "warns", settings["warns"])
            await query.message.edit_text(f"🛡️ User `{target_uid}` whitelisted by {query.from_user.mention}.")
            await query.answer("User whitelisted.")
        else:
            await query.answer("User is already whitelisted.", show_alert=True)

if __name__ == "__main__":
    print("✨ BioLink Protector Bot starting...")
    app.run()
  
