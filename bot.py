import os
import json
from flask import Flask, request
import requests

app = Flask(__name__)

# بيانات البوت والملفات
TELEGRAM_BOT_TOKEN = "8989095746:AAHOl9g15Yt-n8x9R0YgZEPdjhsZjhsKLw8"
BALANCE_FILE = "balance_state.json"

def get_current_balance():
    if not os.path.exists(BALANCE_FILE):
        return 0
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("balance", 0)
    except:
        return 0

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

@app.route("/", methods=["POST"])
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()

    if not update:
        return "OK", 200

    if "callback_query" in update:
        callback = update["callback_query"]
        callback_data = callback.get("data")
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]

        if callback_data == "approve_100_coins":
            new_bal = update_balance(100)
            answer_text = f"✨ تمت العملية بنجاح! إضافة 100 عملة. الرصيد الحالي: {new_bal}"
        elif callback_data == "reject_order":
            answer_text = "❌ تم رفض المعاملة."
        else:
            answer_text = "⚠️ إجراء غير معروف."

        # 1. إيقاف دائرة التحميل للزر وإظهار الإشعار للمستخدم
        requests.post(
            f"https://api.telegram.org/bot8989095746:AAHOl9g15Yt-n8x9R0YgZEPdjhsZjhsKLw8/answerCallbackQuery",
            json={"callback_query_id": callback.get("id"), "text": answer_text}
        )

        # 2. تحديث نص الرسالة وإضافة توقيع الإدارة
        original_caption = callback["message"].get("caption", "")
        updated_caption = original_caption + f"\n\n<b>[تمت المعاملة بواسطة الإدارة]</b>"

        edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageCaption"
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
