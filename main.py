import os
BOT_TOKEN = os.getenv("BOT_TOKEN")  # ✅ Token environment se le raha hai
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing")
import os
import telebot
from flask import Flask, request, abort

# 🔑 Environment variable se token lo  
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 🏠 Health-check route  
@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running ✅", 200

# 🌐 Webhook route for Telegram updates  
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "", 200
    else:
        abort(403)

# ➡️ /start command handler  
@bot.message_handler(commands=["start"])
def send_welcome(message):
    welcome_text = (
        "Hey 🙌 Main tumhara Smart PRNG Market Prediction Bot hoon!\n\n"
        "📩 Mujhe 0–9 tak ke numbers bhejo:\n"
        "`start 2 3 4 5 6 7 8 9 3 1 0 4 5 7 … end`\n\n"
        "Main Big/Small aur Red/Green classify karunga,\n"
        "trend patterns detect karke next safe move suggest karunga 👍"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# ➡️ General text message handler  
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_numbers(message):
    text = message.text.strip().lower()
    # Input format check
    if not text.startswith("start") or not text.endswith("end"):
        bot.reply_to(message, "Format galat hai 😅. \nUse: `start 2 3 4 … end`", parse_mode="Markdown")
        return

    # 🔄 STEP 1 – Extract numbers list  
    parts = text.split()
    try:
        nums = list(map(int, parts[1:-1]))
    except ValueError:
        bot.reply_to(message, "Numbers hi bhejo yaar 🤦‍♂️", parse_mode="Markdown")
        return

    # 🚦 Labels mapping  
    bs_labels = ["Small" if n < 5 else "Big" for n in nums]
    rg_labels = ["Red" if n % 2 == 0 else "Green" for n in nums]

    # 📊 STEP 2 – Recent trends (last 5–15)
    window = nums[-15:] if len(nums) >= 15 else nums
    bs_trend = bs_labels[-len(window):]
    rg_trend = rg_labels[-len(window):]

    # 🔍 STEP 3 – Known patterns definitions
    # (abbreviated for brevity; add all patterns as lists)
    bs_patterns = {
        "Triple": ["Big","Big","Big","Small","Small","Small"],
        "Double": ["Small","Small","Big","Big","Small","Small"],
        "Zigzag": ["Big","Small","Small","Big","Big","Small","Small"],
        # … baaki patterns yahin define karo
    }
    rg_patterns = {
        "Zigzag": ["Red","Green","Green","Red","Red","Green","Green"],
        "Triple": ["Red","Red","Red","Green","Green","Green"],
        # … baaki patterns
    }

    def match_pattern(trend, patterns):
        for name, pat in patterns.items():
            if trend[-len(pat):] == pat:
                return name, pat
        return None, None

    # 🧩 STEP 4 – Pattern match/break/mix
    bs_name, bs_pat = match_pattern(bs_trend, bs_patterns)
    rg_name, rg_pat = match_pattern(rg_trend, rg_patterns)

    def analyze(trend, name, pat):
        result = {}
        result["Trend"] = trend[:10]  # concise
        if name:
            result["Pattern"] = name + " ✅"
            expected = pat[len(trend)%len(pat)]
            found = trend[-1]
            result["Expected"] = expected
            result["Found"] = found
            if found == expected:
                result["Status"] = "Stable 🚀"
            else:
                result["Status"] = "Break ❌"
        else:
            result["Pattern"] = "Mix ⚠️"
            result["Status"] = "Mixed ⚠️"
        return result

    bs_res = analyze(bs_trend, bs_name, bs_pat or [])
    rg_res = analyze(rg_trend, rg_name, rg_pat or [])

    # 🔗 STEP 5 – Cross-analysis simple logic
    if bs_res["Status"].startswith("Stable") and rg_res["Status"].startswith("Stable"):
        suggestion = "🔥 High Confidence (Sniper Entry)"
    elif bs_res["Status"].startswith("Break") or rg_res["Status"].startswith("Break"):
        suggestion = "⚠️ Caution"
    else:
        suggestion = "🛑 Avoid Trade"

    # 📨 Final message assembly
    msg = (
        f"📊 *Big/Small Analysis:*\n"
        f"Trend: {bs_res['Trend']}\n"
        f"Pattern: {bs_res['Pattern']}\n"
        f"Status: {bs_res['Status']}\n\n"
        f"📊 *Red/Green Analysis:*\n"
        f"Trend: {rg_res['Trend']}\n"
        f"Pattern: {rg_res['Pattern']}\n"
        f"Status: {rg_res['Status']}\n\n"
        f"🔎 *Cross Analysis Suggestion:* {suggestion}"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

# 📌 Set webhook on startup
if __name__ == "__main__":
    # Remove existing webhook
    bot.remove_webhook()
    # Set new one to Render URL + token
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # set by Render
    if not RENDER_URL:
        raise RuntimeError("RENDER_EXTERNAL_URL missing")
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
