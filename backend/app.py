
from flask import Flask, request, jsonify, send_file, redirect, url_for
import smtplib
from email.mime.text import MIMEText
import gspread
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__, static_url_path='', static_folder='static')

# Load environment variables
OPENAI_API_KEY = os.getenv("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")
GOOGLE_SHEET_ID = os.getenv("1plCuAgsTi4UTSkuTyuL_ortsRb8W7HyJN0Tg9579LWE")
EMAIL_SENDER = os.getenv("dealofferprodeals@gmail.com")
EMAIL_PASSWORD = os.getenv("lbyq wsna ruok ccfx")

client = OpenAI(api_key="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")

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    client_gc = gspread.authorize(creds)
    return client_gc.open_by_key(GOOGLE_SHEET_ID).sheet1

def send_email_notification(deal_data):
    subject = "📬 New Deal Submitted - Deal Offer Pro"
    body = (
        f"New Deal Submitted:\n"
        f"Seller Name: {deal_data['seller_name']}\n"
        f"Property Address: {deal_data['property_address']}\n"
        f"Deal Type: {deal_data['deal_type']}\n"
        f"Notes: {deal_data['notes']}"
    )
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_SENDER
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def generate_ai_summary(deal_data):
    prompt = (
        f"Analyze this real estate deal and give a quick summary and investment insight:\n"
        f"Seller Name: {deal_data['seller_name']}\n"
        f"Property Address: {deal_data['property_address']}\n"
        f"Deal Type: {deal_data['deal_type']}\n"
        f"Notes: {deal_data['notes']}"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

@app.route('/')
def home():
    try:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'index.html'))
        return send_file(path)
    except Exception as e:
        return f"Error loading homepage: {e}", 500

@app.route('/submit-deal', methods=['POST'])
def submit_deal():
    if request.is_json:
        data = request.get_json()
    else:
        data = {
            "seller_name": request.form.get("seller_name", "Website Lead"),
            "property_address": request.form.get("property_address", ""),
            "deal_type": request.form.get("deal_type", "Analyzer Only"),
            "notes": request.form.get("notes", "")
        }

    print("✅ Deal Received:", data)

    try:
        send_email_notification(data)
    except Exception as e:
        print("❌ Email Error:", e)

    try:
        sheet = get_sheet()
        sheet.append_row([data['seller_name'], data['property_address'], data['deal_type'], data['notes']])
    except Exception as e:
        print("❌ Google Sheets Error:", e)

    try:
        ai_summary = generate_ai_summary(data)
    except Exception as e:
        ai_summary = f"AI Summary error: {e}"

    if request.is_json:
        return jsonify({"message": "Deal submitted successfully", "ai_summary": ai_summary, "data": data}), 200
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

