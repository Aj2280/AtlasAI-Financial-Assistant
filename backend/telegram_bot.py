import os
import sys
import time
import json
import urllib.request
import urllib.parse

# Ensure backend module import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import init_db
from backend.services.memory_service import MemoryService
from backend.services.agent import AgentOrchestrator

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

def telegram_api_call(method: str, params: dict = None, data: bytes = None, headers: dict = None):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN).strip()
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set.")
    url = f"https://api.telegram.org/bot{token}/{method}"
    
    if params:
        url += "?" + urllib.parse.urlencode(params)
        
    req_headers = {"User-Agent": "AtlasTelegramBot/1.0"}
    if headers:
        req_headers.update(headers)
        
    req = urllib.request.Request(url, data=data, headers=req_headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def send_telegram_message(chat_id: int, text: str):
    """Send formatted text response to Telegram user."""
    try:
        telegram_api_call("sendMessage", params={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        })
    except Exception as e:
        # Fallback to plain text if Markdown parsing fails on special characters
        try:
            telegram_api_call("sendMessage", params={
                "chat_id": chat_id,
                "text": text
            })
        except Exception as inner_e:
            print(f"Failed to send Telegram message to {chat_id}: {inner_e}")

def run_polling_loop():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN).strip()
    print("=" * 60)
    print("🤖 ATLAS REAL TELEGRAM BOT CONNECTOR")
    print("=" * 60)
    
    if not token:
        print("\n⚠️  No TELEGRAM_BOT_TOKEN found in environment!")
        return

    # Verify bot identity
    try:
        bot_info = telegram_api_call("getMe")
        print(f"✅ Connected to Real Telegram Bot: @{bot_info['result']['username']} ({bot_info['result']['first_name']})")
    except Exception as e:
        print(f"❌ Failed to verify Telegram Bot Token: {e}")
        return

    init_db()
    print("🚀 Listening for live messages on Telegram... Press CTRL+C to stop.\n")
    
    offset = 0
    while True:
        try:
            updates_data = telegram_api_call("getUpdates", params={"offset": offset, "timeout": 20})
            if not updates_data.get("ok"):
                time.sleep(2)
                continue
                
            updates = updates_data.get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                
                message = update.get("message")
                if not message:
                    continue
                    
                chat_id = message["chat"]["id"]
                display_name = message["from"].get("first_name", "Analyst")
                
                # Register user in database
                user = MemoryService.get_or_create_user(chat_id, display_name)
                
                channel = "text"
                content = ""
                
                if "text" in message:
                    channel = "text"
                    content = message["text"]
                elif "voice" in message:
                    channel = "voice"
                    content = "[Voice Note Received from Telegram]"
                elif "photo" in message or "document" in message:
                    channel = "image"
                    content = "[Financial Document/Photo Received from Telegram]"
                else:
                    continue
                    
                print(f"📩 [{channel.upper()}] From Telegram User {display_name} ({chat_id}): '{content}'")
                
                # Process message through Agent Orchestrator
                res = AgentOrchestrator.process_message(user["id"], content, channel)
                
                # Send reply back to Telegram
                send_telegram_message(chat_id, res["response"])
                print(f"📤 Reply sent back to @{message['from'].get('username', display_name)}")
                
        except KeyboardInterrupt:
            print("\nStopped Telegram Bot listener.")
            break
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_polling_loop()
