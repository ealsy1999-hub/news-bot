import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from rss_parser import fetch_feed, FEEDS
from summarizer import summarize_news, categorize

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

CATEGORIES = {
    "all": ("🌐", "All News"),
    "energy": ("⚡", "Energy"),
    "markets": ("📈", "Markets"),
    "geopolitics": ("🌍", "Geopolitics"),
    "general": ("📰", "General"),
}

CAT_MAP = {
    "all": None,
    "energy": "⚡ Energy",
    "markets": "📈 Markets",
    "geopolitics": "🌍 Geopolitics",
    "general": "📰 General",
}

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🌐 Full Digest", callback_data="digest_all"),
            InlineKeyboardButton("⚡ Energy", callback_data="digest_energy"),
        ],
        [
            InlineKeyboardButton("📈 Markets", callback_data="digest_markets"),
            InlineKeyboardButton("🌍 Geopolitics", callback_data="digest_geopolitics"),
        ],
        [
            InlineKeyboardButton("📰 General", callback_data="digest_general"),
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("← Back to Menu", callback_data="menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Welcome to News Digest Bot*\n\n"
        "Your personal AI-powered digest of global energy, markets & geopolitics news.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🤖 Powered by Groq AI\n"
        "📡 Sources: OilPrice · MarketWatch · Seeking Alpha · NGI\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Choose a category below 👇"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu())

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Your Chat ID: `{chat_id}`", parse_mode="Markdown")

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        text = "📰 *News Digest Bot*\n\nChoose a category 👇"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu())
        return

    if query.data == "about":
        text = (
            "ℹ️ *About News Digest Bot*\n\n"
            "This bot fetches the latest news from top financial and energy sources, "
            "then uses Groq AI (Llama 3) to summarize each article into a clear, "
            "analytical digest.\n\n"
            "📡 *Sources:*\n"
            "• OilPrice.com\n"
            "• MarketWatch\n"
            "• Seeking Alpha Energy\n"
            "• Natural Gas Intelligence\n\n"
            "🤖 *AI Model:* Llama 3.1 8B (Groq)\n"
            "⚡ *Update frequency:* On demand + daily at 6:00 MSK"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_menu())
        return

    if query.data.startswith("digest_"):
        cat_key = query.data.replace("digest_", "")
        emoji, label = CATEGORIES[cat_key]
        filter_cat = CAT_MAP[cat_key]

        await query.edit_message_text(
            f"⏳ *Fetching {label} news...*\n\nThis may take 20-30 seconds while AI summarizes articles.",
            parse_mode="Markdown"
        )

        all_news = []
        for name, url in FEEDS.items():
            items = fetch_feed(name, url, max_items=8)
            all_news.extend(items)

        if filter_cat:
            all_news = [n for n in all_news if categorize(n["title"]) == filter_cat]

        if not all_news:
            await query.edit_message_text(
                f"😔 No {label} news found right now.\nTry again later.",
                reply_markup=back_menu()
            )
            return

        grouped = {}
        for item in all_news[:12]:
            cat = categorize(item["title"])
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(item)

        header = f"{emoji} *{label} Digest*\n"
        header += f"━━━━━━━━━━━━━━━━━━\n"
        header += f"📊 {len(all_news)} stories · AI-summarized\n"
        header += f"━━━━━━━━━━━━━━━━━━\n\n"

        await query.edit_message_text(header, parse_mode="Markdown")

        for cat, items in grouped.items():
            section = f"*{cat}*\n\n"
            for item in items[:3]:
                summary = summarize_news(item["title"], item["summary"], item["source"])
                section += f"📌 *{item['title']}*\n"
                section += f"_{item['source']}_\n\n"
                section += f"{summary}\n\n"
                section += f"[→ Read full article]({item['link']})\n"
                section += "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n\n"

            chunks = [section[i:i+4000] for i in range(0, len(section), 4000)]
            for chunk in chunks:
                await query.message.reply_text(
                    chunk,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )

        await query.message.reply_text(
            "✅ *Digest complete!*\n\nWant more news?",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

async def digest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📰 *News Digest Bot*\n\nChoose a category 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

async def send_daily_digest(app):
    chat_id = os.getenv("MY_CHAT_ID")
    if not chat_id:
        return

    all_news = []
    for name, url in FEEDS.items():
        items = fetch_feed(name, url, max_items=8)
        all_news.extend(items)

    header = "🌅 *Good morning! Your Daily Digest*\n━━━━━━━━━━━━━━━━━━\n\n"
    await app.bot.send_message(chat_id=chat_id, text=header, parse_mode="Markdown")

    grouped = {}
    for item in all_news[:15]:
        cat = categorize(item["title"])
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)

    for cat, items in grouped.items():
        section = f"*{cat}*\n\n"
        for item in items[:3]:
            summary = summarize_news(item["title"], item["summary"], item["source"])
            section += f"📌 *{item['title']}*\n_{item['source']}_\n\n{summary}\n\n[→ Read]({item['link']})\n┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n\n"

        chunks = [section[i:i+4000] for i in range(0, len(section), 4000)]
        for chunk in chunks:
            await app.bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown", disable_web_page_preview=True)

    await app.bot.send_message(chat_id=chat_id, text="✅ *Daily digest complete!*", parse_mode="Markdown", reply_markup=main_menu())

def schedule_daily(app):
    import threading
    from datetime import datetime, timezone, timedelta
    import time

    MSK = timezone(timedelta(hours=3))

    def run():
        while True:
            now = datetime.now(MSK)
            target = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if now >= target:
                target += timedelta(days=1)
            wait = (target - now).total_seconds()
            print(f"⏰ Next digest at 06:00 MSK — waiting {int(wait//3600)}h {int((wait%3600)//60)}m")
            time.sleep(wait)
            asyncio.run(send_daily_digest(app))

    t = threading.Thread(target=run, daemon=True)
    t.start()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("digest", digest_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CallbackQueryHandler(menu_callback))
    schedule_daily(app)
    print("✓ Bot is running with daily digest at 06:00 MSK...")
    app.run_polling()

if __name__ == "__main__":
    main()
