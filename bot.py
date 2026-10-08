import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telegram import InlineKeyboardButton as Btn
from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

import data

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME", "Football Hub")

CAMBODIA_TZ = timezone(timedelta(hours=7))  # ICT, no daylight saving

RANK_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


# ---------- Keyboards ----------

def kb(*rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([list(r) for r in rows])


HOME_BTN = Btn("🏠 ទំព័រដើម", callback_data="home")


def home_kb():
    return kb(
        [Btn("🔴 ប្រកួតបន្តផ្ទាល់", callback_data="live"), Btn("📊 លទ្ធផល", callback_data="results")],
        [Btn("📅 កាលវិភាគ", callback_data="fixtures"), Btn("📰 ព័ត៌មាន", callback_data="news")],
        [Btn("🏆 តារាងពិន្ទុ", callback_data="tables"), Btn("⚙️ ការកំណត់", callback_data="settings")],
    )


def refresh_kb(section):
    return kb([Btn("🔄 ធ្វើបច្ចុប្បន្នភាព", callback_data=f"refresh:{section}")], [HOME_BTN])


def news_kb():
    return kb([Btn("📖 អានបន្ថែម", url=data.NEWS_URL)], [HOME_BTN])


def leagues_kb():
    items = [Btn(lg["name"], callback_data=f"table:{key}") for key, lg in data.LEAGUES.items()]
    rows = [items[i:i + 2] for i in range(0, len(items), 2)]
    return kb(*rows, [HOME_BTN])


def table_kb():
    return kb([Btn("⬅️ ជ្រើសលីគផ្សេង", callback_data="tables")], [HOME_BTN])


def settings_kb(notify_on):
    bell = "🔔 ការជូនដំណឹង: បើក ✅" if notify_on else "🔕 ការជូនដំណឹង: បិទ ❌"
    return kb(
        [Btn(bell, callback_data="set:notify")],
        [Btn("🌐 ភាសា", callback_data="set:lang")],
        [Btn("ℹ️ អំពី Bot", callback_data="set:about")],
        [HOME_BTN],
    )


def lang_kb():
    return kb(
        [Btn("🇰🇭 ខ្មែរ ✅", callback_data="lang:km"), Btn("🇬🇧 English", callback_data="lang:en")],
        [Btn("⬅️ ត្រឡប់ក្រោយ", callback_data="settings")],
    )


def back_settings_kb():
    return kb([Btn("⬅️ ត្រឡប់ក្រោយ", callback_data="settings")], [HOME_BTN])


# ---------- Screens (text) ----------

def home_text():
    return (
        f"⚽️ <b>សូមស្វាគមន៍មកកាន់ {BOT_NAME}</b>\n\n"
        "តាមដានព័ត៌មានបាល់ទាត់ លទ្ធផល កាលវិភាគ និងការប្រកួតបន្តផ្ទាល់ពីជុំវិញពិភពលោក 🌍\n\n"
        "👇 <b>សូមជ្រើសរើសខាងក្រោម</b>"
    )


def live_text():
    if not data.LIVE_MATCHES:
        return "🔴 <b>ប្រកួតបន្តផ្ទាល់</b>\n\nមិនមានការប្រកួតកំពុងលេងនៅពេលនេះទេ។"
    blocks = [
        f"🔴 <b>LIVE</b>\n⚽️ {m['home']} <b>{m['score']}</b> {m['away']}\n⏱️ {m['minute']}"
        for m in data.LIVE_MATCHES
    ]
    return "\n\n".join(blocks)


def results_text():
    lines = [f"⚽️ {m['home']} <b>{m['score']}</b> {m['away']}" for m in data.RESULTS]
    return "📊 <b>លទ្ធផលថ្ងៃនេះ</b>\n\n" + "\n".join(lines)


def fixtures_text():
    blocks = [f"⚽️ {m['home']} 🆚 {m['away']}\n🕐 {m['time']}" for m in data.FIXTURES]
    return "📅 <b>ការប្រកួតបន្ទាប់</b>\n\n" + "\n\n".join(blocks)


def news_text():
    return (
        "📰 <b>ព័ត៌មានបាល់ទាត់ថ្មីៗ</b>\n\n"
        "🔥 ព័ត៌មានថ្មីៗពីក្រុម និងកីឡាករល្បីៗ\n"
        "⚽️ ព័ត៌មានការផ្ទេរកីឡាករ\n"
        "🏆 ព័ត៌មានពីលីគ និងការប្រកួតធំៗ"
    )


def tables_text():
    return "🏆 <b>តារាងពិន្ទុ</b>\n\nសូមជ្រើសរើសលីគ 👇"


def table_text(key):
    league = data.LEAGUES[key]
    lines = [
        f"{RANK_EMOJI[i]} {team} — <b>{pts} pts</b>"
        for i, (team, pts) in enumerate(league["table"])
    ]
    return f"<b>{league['name']}</b>\n\n" + "\n".join(lines)


def settings_text():
    return "⚙️ <b>ការកំណត់</b>\n\nសូមជ្រើសរើសខាងក្រោម 👇"


def lang_text():
    return "🌐 <b>ភាសា</b>\n\nសូមជ្រើសរើសភាសា 👇"


def about_text():
    return (
        f"ℹ️ <b>អំពី {BOT_NAME}</b>\n\n"
        "Bot សម្រាប់តាមដានព័ត៌មានបាល់ទាត់ ⚽️\n"
        "🔴 ប្រកួតបន្តផ្ទាល់\n📊 លទ្ធផល\n📅 កាលវិភាគ\n📰 ព័ត៌មាន\n🏆 តារាងពិន្ទុ\n\n"
        "📌 Version 1.0"
    )


# ---------- Handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        home_text(),
        parse_mode=ParseMode.HTML,
        reply_markup=home_kb(),
    )


async def show(query, text, markup):
    try:
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
    except BadRequest as e:
        # Pressing 🔄 when nothing changed — ignore
        if "not modified" not in str(e).lower():
            raise


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    action = query.data
    notify_on = context.user_data.get("notify", False)

    if action == "set:notify":
        notify_on = not notify_on
        context.user_data["notify"] = notify_on
        await query.answer("🔔 បានបើកការជូនដំណឹង" if notify_on else "🔕 បានបិទការជូនដំណឹង")
        await show(query, settings_text(), settings_kb(notify_on))
        return

    if action == "lang:en":
        await query.answer("🇬🇧 English នឹងមកដល់ឆាប់ៗ!", show_alert=True)
        return

    if action == "lang:km":
        await query.answer("🇰🇭 អ្នកកំពុងប្រើភាសាខ្មែរ")
        return

    if action.startswith("refresh:"):
        section = action.split(":", 1)[1]
        text_fn = {"live": live_text, "results": results_text, "fixtures": fixtures_text}.get(section)
        if text_fn:
            now = datetime.now(CAMBODIA_TZ).strftime("%H:%M:%S")
            await query.answer("✅ បានធ្វើបច្ចុប្បន្នភាព")
            await show(query, f"{text_fn()}\n\n🕐 <i>បានធ្វើបច្ចុប្បន្នភាព: {now}</i>", refresh_kb(section))
        return

    await query.answer()

    if action.startswith("table:"):
        key = action.split(":", 1)[1]
        if key in data.LEAGUES:
            await show(query, table_text(key), table_kb())
        return

    screens = {
        "home": (home_text, home_kb),
        "live": (live_text, lambda: refresh_kb("live")),
        "results": (results_text, lambda: refresh_kb("results")),
        "fixtures": (fixtures_text, lambda: refresh_kb("fixtures")),
        "news": (news_text, news_kb),
        "tables": (tables_text, leagues_kb),
        "settings": (settings_text, lambda: settings_kb(notify_on)),
        "set:lang": (lang_text, lang_kb),
        "set:about": (about_text, back_settings_kb),
    }
    if action in screens:
        text_fn, kb_fn = screens[action]
        await show(query, text_fn(), kb_fn())


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Missing BOT_TOKEN. Put it in a .env file (see .env.example).")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler(["start", "menu"], start))
    app.add_handler(CallbackQueryHandler(on_button))

    print(f"⚽️ {BOT_NAME} (KH) is running... (Ctrl+C to stop)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
