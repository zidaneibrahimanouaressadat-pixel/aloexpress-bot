import json
import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8989095746:AAHOl9g15Yt-n8x9R0YgZEPdjhsZjhsKLw8"
TELEGRAM_CHAT_ID = "6407578544"
BALANCE_FILE = "balance_state.json"

def get_current_balance():
    if not os.path.exists(BALANCE_FILE):
        return 50
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("balance", 50)
    except:
        return 50

def update_balance(amount_to_add):
    current = get_current_balance()
    new_balance = current + amount_to_add
    data = {
        "balance": new_balance,
        "last_updated": "2026-03-20"
    }
    with open(BALANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return new_balance

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    
    if "callback_query" in update:
        callback = update["callback_query"]
        callback_data = callback.get("data")
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        
        if callback_data == "approve_100_coins":
            new_bal = update_balance(100)
            answer_text = f"✅ تم قبول المعاملة بنجاح! إضافة 100 عملة. الرصيد الحالي: {new_bal} عملة."
        elif callback_data == "reject_order":
            answer_text = "❌ تم رفض المعاملة."
        else:
            answer_text = "⚠️ إجراء غير معروف."

        # الرد على ضغطة الزر في تيليجرام
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
        requests.post(url, json={"callback_query_id": callback["id"], "text": answer_text, "show_alert": True})
        
        # تعديل رسالة البوت لإظهار أن الطلب تمت معالجته
        edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageCaption"
        original_caption = callback["message"].get("caption", "")
        updated_caption = original_caption + f"\n\n<b>[حالة الطلب: تمت المعاملة بواسطة الإدارة]</b>"
        
        requests.post(edit_url, json={
            "chat_id": chat_id,
            "message_id": message_id,
            "caption": updated_caption,
            "parse_mode": "HTML"
        })

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
