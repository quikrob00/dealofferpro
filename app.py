from flask import Flask, request, jsonify, render_template_string
import smtplib
from email.mime.text import MIMEText
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# Google Sheets setup
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    return sheet

# Email notification
def send_email_notification(deal_data):
    subject = "📬 New Deal Submitted - Deal Offer Pro"
    body = f"""
New Deal Submitted:

Seller Name: {deal_data['seller_name']}
Property Address: {deal_data['property_address']}
Deal Type: {deal_data['deal_type']}
Notes: {deal_data['notes']}

🔥 Deal Offer Pro
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_SENDER

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# AI analysis
def generate_ai_summary(deal_data):
    prompt = f"""
Analyze this real estate deal and give a quick summary and investment insight:

Seller Name: {deal_data['seller_name']}
Property Address: {deal_data['property_address']}
Deal Type: {deal_data['deal_type']}
Notes: {deal_data['notes']}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()

# Homepage
@app.route('/')
def home():
    return "✅ Deal Offer Pro - Phase 3 is LIVE!"

# HTML Form
@app.route('/form')
def form():
    return render_template_string("""
    <html>
    <head><title>Submit Deal - Deal Offer Pro</title></head>
    <body>
    <h1>Submit Your Deal</h1>
    <form method="POST" action="/submit-deal">
        Seller Name:<br><input name="seller_name"><br>
        Property Address:<br><input name="property_address"><br>
        Deal Type:<br>
        <select name="deal_type">
            <option value="Cash">Cash</option>
            <option value="Novation">Novation</option>
            <option value="Section 8">Section 8</option>
            <option value="Seller Finance">Seller Finance</option>
        </select><br>
        Notes:<br><textarea name="notes"></textarea><br><br>
        <input type="submit" value="Submit Deal">
    </form>
    </body>
    </html>
    """)

# Deal Submission Route
@app.route('/submit-deal', methods=['POST'])
def submit_deal():
    if request.is_json:
        data = request.get_json()
    else:
        data = {
            "seller_name": request.form.get("seller_name"),
            "property_address": request.form.get("property_address"),
            "deal_type": request.form.get("deal_type"),
            "notes": request.form.get("notes")
        }

    # 1. Email Notification
    send_email_notification(data)

    # 2. Google Sheets Sync
    try:
        sheet = get_sheet()
        sheet.append_row([data['seller_name'], data['property_address'], data['deal_type'], data['notes']])
    except Exception as e:
        print("❌ Google Sheets Error:", e)

    # 3. AI Deal Summary
    try:
        ai_summary = generate_ai_summary(data)
    except Exception as e:
        ai_summary = f"AI Summary error: {e}"

    return jsonify({
        "message": "✅ Deal submitted successfully!",
        "ai_summary": ai_summary,
        "data": data
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
