import logging
import os
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚠️ THAY MÃ TOKEN CỦA BẠN VÀO GIỮA HAI DẤU NGOẶC KÉP
TOKEN = "8612923933:AAHLC4b6TJXueedPqlIcE4fY5kiKnPA_tOA"

# --- ĐOẠN CODE PHỤ TRỢ ĐỂ TREO 24/24 TRÊN RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()
# --------------------------------------------------

def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id
    if context.args:
        try: return int(context.args)
        except ValueError: return None
    return None

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ Vui lòng reply hoặc gõ: /ban [User_ID]")
        return
    try:
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await update.message.reply_text(f"🚫 Đã BAN thành viên có ID: {user_id}")
    except Exception as e: await update.message.reply_text(f"❌ Lỗi: {e}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ Vui lòng reply hoặc gõ: /unban [User_ID]")
        return
    try:
        await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id, only_if_banned=True)
        await update.message.reply_text(f"✅ Đã UNBAN thành viên có ID: {user_id}")
    except Exception as e: await update.message.reply_text(f"❌ Lỗi: {e}")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ Vui lòng reply hoặc gõ: /mute [User_ID]")
        return
    try:
        mute_duration = datetime.now(timezone.utc) + timedelta(minutes=36)
        
        # ĐÃ SỬA LỖI: Chỉ dùng can_send_messages=False để chặn toàn bộ chat/media
        permissions = ChatPermissions(can_send_messages=False)
        
        await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions, until_date=mute_duration)
        await update.message.reply_text(f"🔇 Đã MUTE thành viên {user_id} trong 36 phút.")
    except Exception as e: await update.message.reply_text(f"❌ Lỗi: {e}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = get_user_id(update, context)
    if not user_id:
        await update.message.reply_text("❌ Vui lòng reply hoặc gõ: /unmute [User_ID]")
        return
    try:
        # ĐÃ SỬA LỖI: Trả lại quyền chat cơ bản tương thích v20+
        permissions = ChatPermissions(
            can_send_messages=True, 
            can_send_polls=True, 
            can_send_other_messages=True, 
            can_add_web_page_previews=True
        )
        await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=permissions)
        await update.message.reply_text(f"🔊 Đã UNMUTE thành viên có ID: {user_id}")
    except Exception as e: await update.message.reply_text(f"❌ Lỗi: {e}")

def main():
    threading.Thread(target=run_health_check_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    print("Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
    