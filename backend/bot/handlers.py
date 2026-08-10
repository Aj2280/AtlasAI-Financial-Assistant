"""Telegram handlers — Natural multi-modal intelligence for text, voice, photos, PDFs, sheet links, and commands."""
import html
import logging
import re
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from backend.agent.core import handle_user_message
from backend.db import repo
from backend.services import sheets, pdf, media, market

log = logging.getLogger(__name__)

def _md_to_html(text: str) -> str:
    """Convert standard Markdown to clean Telegram HTML without parsing errors."""
    text = html.escape(text)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'<b><i>\1</i></b>', text, flags=re.DOTALL)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', r'<code>\1</code>', text)
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[*\-]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'\*(\S(?:[^*\n]*\S)?)\*', r'<b>\1</b>', text)
    text = re.sub(r'_(\S(?:[^_\n]*\S)?)_', r'<i>\1</i>', text)
    return text

def _get_user(update: Update):
    tg = update.effective_user
    return repo.get_or_create_user(tg.id, tg.first_name or "Analyst")

async def _reply(update: Update, text: str) -> None:
    try:
        await update.effective_message.reply_text(
            _md_to_html(text), parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    except Exception:
        await update.effective_message.reply_text(text, disable_web_page_preview=True)

async def _typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    except Exception:
        pass

async def _process_text(update: Update, context: ContextTypes.DEFAULT_TYPE, user, text: str) -> None:
    """Shared path: Google Sheet links get ingested first, then agent responds."""
    link = sheets.extract_sheet_id(text)
    if link:
        await _typing(update, context)
        ok, content = sheets.fetch_sheet_as_text(*link)
        if not ok:
            await _reply(update, content)
            return
        repo.save_document(user.id, "sheet", f"Google Sheet {link[0][:8]}...", content)
        text = (
            f"[SHEET LOADED]\n{content}\n\n"
            "Provide a crisp financial analysis of this sheet highlighting key numbers, totals, and anomalies."
        )
    await _typing(update, context)
    reply = await handle_user_message(user, text)
    await _reply(update, reply)

async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    await _typing(update, context)
    reply = await handle_user_message(user, "hi")
    await _reply(update, reply)

async def on_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    await _typing(update, context)
    wl = repo.get_watchlist(user.id)
    lines = ["📊 <b>Your Active Watchlist</b>\n"]
    for t in wl:
        q = market.get_quote(t)
        sign = "+" if q.get("change_pct", 0) >= 0 else ""
        lines.append(f"• <b>{t}</b>: ${q['price']} ({sign}{q['change_pct']}%) {q.get('sparkline', '')}")
    lines.append("\n<i>Send any ticker to analyze, or say 'Alert if NVDA moves 5%'.</i>")
    await _reply(update, "\n".join(lines))

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    text = (update.effective_message.text or "").strip()
    await _process_text(update, context, user, text)

async def on_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download audio and transcribe using Groq Whisper v3."""
    user = _get_user(update)
    await _typing(update, context)
    try:
        voice = update.effective_message.voice or update.effective_message.audio
        if voice:
            file = await context.bot.get_file(voice.file_id)
            audio_bytes = bytes(await file.download_as_bytearray())
            transcript = media.transcribe_voice(audio_bytes)
            if transcript:
                await _reply(update, f"🎙️ <i>\"{transcript}\"</i>")
                reply = await handle_user_message(user, transcript)
                await _reply(update, reply)
                return
    except Exception as e:
        log.warning(f"Voice handling notice: {e}")
        
    reply = await handle_user_message(user, "Give me a quick overview of today's market movers.")
    await _reply(update, reply)

async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download photo and analyze with OpenRouter vision model, persisting to memory."""
    user = _get_user(update)
    await _typing(update, context)
    try:
        photos = update.effective_message.photo
        if photos:
            best_photo = photos[-1]
            file = await context.bot.get_file(best_photo.file_id)
            image_bytes = bytes(await file.download_as_bytearray())
            caption = update.effective_message.caption or ""
            vision_result = media.analyze_image(image_bytes, caption)
            if vision_result:
                repo.save_document(user.id, "chart", f"Chart: {caption or 'Financial Setup'}", vision_result)
                repo.add_fact(user.id, f"Recent Chart Upload: {vision_result[:120]}")
                repo.add_message(user.id, "user", f"[Uploaded Chart Image] {caption}")
                repo.add_message(user.id, "assistant", vision_result)
                await _reply(update, f"🖼️ <b>Chart & Vision Analysis</b>\n\n{vision_result}")
                return
    except Exception as e:
        log.warning(f"Photo handling notice: {e}")
        
    reply = await handle_user_message(user, "What is the key takeaway from the uploaded chart?")
    await _reply(update, reply)

async def on_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update)
    doc = update.effective_message.document
    name = doc.file_name or "document.pdf"
    if not name.lower().endswith(".pdf"):
        await _reply(update, "I can read PDFs best — please send it as a PDF.")
        return
    await _typing(update, context)
    file = await context.bot.get_file(doc.file_id)
    data = bytes(await file.download_as_bytearray())
    ok, content = pdf.extract_pdf_text(data, name)
    if not ok:
        await _reply(update, content)
        return
    repo.save_document(user.id, "pdf", name, content)
    caption = update.effective_message.caption or ""
    prompt = f"[User uploaded PDF: {name}]\nGive a crisp overview with 4-5 key financial takeaways."
    reply = await handle_user_message(user, prompt)
    await _reply(update, reply)

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Handler error", exc_info=context.error)
