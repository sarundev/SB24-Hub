import html
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import InlineKeyboardButton as Btn
from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

import data
from football_api import CAMBODIA_TZ, FootballAPIError, FootballData

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME", "Football Hub")

# Free key from https://www.football-data.org/client/register — without it the bot shows demo data
api = FootballData(os.getenv("FOOTBALL_DATA_KEY"))

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("football_hub")

MAX_MATCHES = 20
ERROR_TEXT = "⚠️ មិនអាចទាញទិន្នន័យបានទេនៅពេលនេះ។ សូមព្យាយាមម្តងទៀតបន្តិចទៀត។"
DEMO_NOTE = "\n\n<i>⚠️ ទិន្នន័យគំរូ (Demo)</i>"

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


def team(name):
    return html.escape(name)


def grouped(matches, line_fn):
    """Group matches under their league heading, in the same order as the league menu."""
    shown = matches[:MAX_MATCHES]
    blocks = []
    for code, name in data.COMPETITION_NAMES.items():
        lines = [line_fn(m) for m in shown if m["comp"] == code]
        if lines:
            blocks.append(f"<b>{name}</b>\n" + "\n\n".join(lines))
    if len(matches) > MAX_MATCHES:
        blocks.append(f"<i>… និង {len(matches) - MAX_MATCHES} ប្រកួតទៀត</i>")
    return "\n\n".join(blocks)


async def live_text():
    title = "🔴 <b>ប្រកួតបន្តផ្ទាល់</b>\n\n"
    matches = await api.live()
    if not matches:
        return title + "មិនមានការប្រកួតកំពុងលេងនៅពេលនេះទេ។"
    return title + grouped(matches, lambda m: (
        f"🔴 <b>LIVE</b>\n⚽️ {team(m['home'])} <b>{m['score']}</b> {team(m['away'])}\n⏱️ {m['minute']}"
    ))


async def results_text():
    title = "📊 <b>លទ្ធផលចុងក្រោយ</b>\n\n"
    matches = await api.results()
    if not matches:
        return title + "មិនមានលទ្ធផលក្នុង ៣ ថ្ងៃចុងក្រោយទេ។"
    return title + grouped(matches, lambda m: (
        f"⚽️ {team(m['home'])} <b>{m['score']}</b> {team(m['away'])} <i>({m['date']})</i>"
    ))


async def fixtures_text():
    title = "📅 <b>ការប្រកួតបន្ទាប់</b>\n\n"
    matches = await api.fixtures()
    if not matches:
        return title + "មិនមានការប្រកួតក្នុង ៣ ថ្ងៃខាងមុខទេ។"
    return title + grouped(matches, lambda m: (
        f"⚽️ {team(m['home'])} 🆚 {team(m['away'])}\n🕐 {m['time']}"
    ))


def news_text():
    return (
        "📰 <b>ព័ត៌មានបាល់ទាត់ថ្មីៗ</b>\n\n"
        "🔥 ព័ត៌មានថ្មីៗពីក្រុម និងកីឡាករល្បីៗ\n"
        "⚽️ ព័ត៌មានការផ្ទេរកីឡាករ\n"
        "🏆 ព័ត៌មានពីលីគ និងការប្រកួតធំៗ"
    )


def tables_text():
    return "🏆 <b>តារាងពិន្ទុ</b>\n\nសូមជ្រើសរើសលីគ 👇"


async def table_text(key):
    league = data.LEAGUES[key]
    rows = (await api.table(league["code"]))[:len(RANK_EMOJI)]
    if not rows:
        return f"<b>{league['name']}</b>\n\nមិនទាន់មានតារាងពិន្ទុនៅឡើយទេ។"
    lines = []
    for i, (name, pts, played) in enumerate(rows):
        line = f"{RANK_EMOJI[i]} {team(name)} — <b>{pts} pts</b>"
        if played is not None:
            line += f" <i>({played} ប្រកួត)</i>"
        lines.append(line)
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
        "📡 ទិន្នន័យពី football-data.org\n"
        "📌 Version 1.1"
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


DATA_SECTIONS = {"live": live_text, "results": results_text, "fixtures": fixtures_text}


async def load(text_fn):
    """Build a screen that needs API data; show a friendly message if the API fails."""
    try:
        text = await text_fn()
    except FootballAPIError as e:
        log.warning("football-data.org error: %s", e)
        return ERROR_TEXT
    return text + DEMO_NOTE if api.demo else text


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

    if action.startswith("refresh:") or action in DATA_SECTIONS:
        refreshing = action.startswith("refresh:")
        section = action.split(":", 1)[1] if refreshing else action
        text_fn = DATA_SECTIONS.get(section)
        if not text_fn:
            await query.answer()
            return
        await query.answer("✅ បានធ្វើបច្ចុប្បន្នភាព" if refreshing else None)
        text = await load(text_fn)
        if refreshing:
            now = datetime.now(CAMBODIA_TZ).strftime("%H:%M:%S")
            text += f"\n\n🕐 <i>បានធ្វើបច្ចុប្បន្នភាព: {now}</i>"
        await show(query, text, refresh_kb(section))
        return

    await query.answer()

    if action.startswith("table:"):
        key = action.split(":", 1)[1]
        if key in data.LEAGUES:
            await show(query, await load(lambda: table_text(key)), table_kb())
        return

    screens = {
        "home": (home_text, home_kb),
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

    mode = "DEMO data (no FOOTBALL_DATA_KEY)" if api.demo else "live data from football-data.org"
    print(f"⚽️ {BOT_NAME} (KH) is running with {mode}... (Ctrl+C to stop)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
