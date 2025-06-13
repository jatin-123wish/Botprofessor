import os
import telebot
from flask import Flask, request, abort

# 🔑 Get token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable missing")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Global dictionary to store each user's historical market numbers.
# Key: chat id; Value: list of numbers.
user_chains = {}

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
        "📩 Mujhe historical data bhejne ke liye use karo:\n"
        "`start 2 3 4 5 6 7 8 9 3 1 0 4 5 7 ... end`\n\n"
        "Uske baad, jab bhi market update mile, bas ek ya zyada numbers bhejo.\n"
        "Main Big/Small aur Red calculate karke,\n"
        "pattern analysis aur suggestion ke saath answer dunga 👍"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# ➡️ General text message handler
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_numbers(message):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    
    # Check if the message is the initial historical data (using "start ... end")
    if text.startswith("start") and text.endswith("end"):
        parts = text.split()
        try:
            # Extract numbers from the full chain sent between "start" and "end"
            nums = list(map(int, parts[1:-1]))
        except ValueError:
            bot.reply_to(message, "Numbers hi bhejo yaar 🤦‍♂️", parse_mode="Markdown")
            return
        # Save (or reset) the chain for this user
        user_chains[chat_id] = nums
    else:
        # Otherwise, assume the message a feedback update containing one or more numbers
        try:
            new_nums = list(map(int, text.split()))
            if chat_id in user_chains:
                user_chains[chat_id].extend(new_nums)
            else:
                bot.reply_to(message, "Pehle historical data bhejo - format: start 2 3 4 ... end", parse_mode="Markdown")
                return
        except ValueError:
            bot.reply_to(message, "Format galat hai. Use full data: start ... end or simply send market number(s) as feedback.", parse_mode="Markdown")
            return

    # Use the historical chain for further analysis
    chain = user_chains[chat_id]
    total = len(chain)
    if total == 0:
        bot.reply_to(message, "Koi data nahi mila.", parse_mode="Markdown")
        return

    # Calculate Market Number percentage based on the latest number.
    # (Since numbers are assumed 0-9, we scale the last number to a percentage).
    last_num = chain[-1]
    market_num_pct = round((last_num / 9) * 100, 2)

    # Calculate Big/Small frequency:
    # Using our definition: numbers < 5 → "Small", >= 5 → "Big"
    big_count = sum(1 for n in chain if n >= 5)
    small_count = total - big_count
    big_pct = round((big_count / total) * 100, 2)
    small_pct = round((small_count / total) * 100, 2)
    # Select dominant label based on which percentage is higher
    dominant_bs = "Big" if big_pct >= small_pct else "Small"
    bs_dom_pct = big_pct if big_pct >= small_pct else small_pct

    # Calculate Red/Green frequency:
    # Using our definition: even → "Red", odd → "Green"
    red_count = sum(1 for n in chain if n % 2 == 0)
    green_count = total - red_count
    red_pct = round((red_count / total) * 100, 2)
    green_pct = round((green_count / total) * 100, 2)
    dominant_rg = "Red" if red_pct >= green_pct else "Green"
    rg_dom_pct = red_pct if red_pct >= green_pct else green_pct

    # For pattern analysis, use the most recent 15 numbers (or fewer if not available)
    window = chain[-15:] if total >= 15 else chain[:]
    bs_labels = ["Small" if n < 5 else "Big" for n in window]
    rg_labels = ["Red" if n % 2 == 0 else "Green" for n in window]

    # Define known patterns for Big/Small and Red/Green (you can refine or add more patterns)
    bs_patterns = {
        "Triple": ["Big", "Big", "Big", "Small", "Small", "Small"],
        "Double": ["Small", "Small", "Big", "Big", "Small", "Small"],
        "Zigzag": ["Big", "Small", "Small", "Big", "Big", "Small", "Small"],
    }
    rg_patterns = {
        "Zigzag": ["Red", "Green", "Green", "Red", "Red", "Green", "Green"],
        "Triple": ["Red", "Red", "Red", "Green", "Green", "Green"],
    }

    def match_pattern(trend, patterns):
        for name, pat in patterns.items():
            if len(trend) >= len(pat) and trend[-len(pat):] == pat:
                return name, pat
        return None, None

    bs_name, bs_pat = match_pattern(bs_labels, bs_patterns)
    rg_name, rg_pat = match_pattern(rg_labels, rg_patterns)

    def analyze(trend, name, pat):
        result = {}
        result["Trend"] = trend
        if name:
            result["Pattern"] = name + " ✅"
            # A sample expected value based on cycle (if pattern length > 0)
            expected = pat[len(trend) % len(pat)] if len(pat) > 0 else None
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

    bs_res = analyze(bs_labels, bs_name, bs_pat or [])
    rg_res = analyze(rg_labels, rg_name, rg_pat or [])

    # Cross-analysis for final trade suggestion
    if bs_res["Status"].startswith("Stable") and rg_res["Status"].startswith("Stable"):
        suggestion = "🔥 High Confidence (Sniper Entry)"
    elif bs_res["Status"].startswith("Break") or rg_res["Status"].startswith("Break"):
        suggestion = "⚠️ Caution"
    else:
        suggestion = "🛑 Avoid Trade"

    # Compose the final output message in the desired format:
    #  • Market Number as a percentage (derived from the latest number)
    #  • Dominant Big/Small percentage  
    #  • Dominant Red/Green percentage  
    #  • Trade suggestion along with pattern details
    msg = (
        f"📈 *Market Number:* {market_num_pct}% (Last: {last_num})\n"
        f"📊 *Big/Small:* {dominant_bs} ({bs_dom_pct}%)\n"
        f"🌈 *Red/Green:* {dominant_rg} ({rg_dom_pct}%)\n"
        f"💡 *Trade Suggestion:* {suggestion}\n\n"
        f"💬 *Pattern Analysis:*\n"
        f"• Big/Small Trend: {bs_labels}\n"
        f"  Pattern: {bs_res['Pattern']}, Status: {bs_res['Status']}\n"
        f"• Red/Green Trend: {rg_labels}\n"
        f"  Pattern: {rg_res['Pattern']}, Status: {rg_res['Status']}"
    )
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# 📌 Set webhook on startup
if __name__ == "__main__":
    # Remove existing webhook
    bot.remove_webhook()
    # Get the Render URL from environment variable (set by Render)
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if not RENDER_URL:
        raise RuntimeError("RENDER_EXTERNAL_URL missing")
    webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
