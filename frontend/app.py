from flask import Flask, request, jsonify, render_template_string, redirect, url_for
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

openai.api_key = OPENAI_API_KEY

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID).sheet1

def send_email_notification(deal_data):
    subject = "📬 New Deal Submitted - Deal Offer Pro"
    body = f"""New Deal Submitted:
Seller Name: {deal_data['seller_name']}
Property Address: {deal_data['property_address']}
Deal Type: {deal_data['deal_type']}
Notes: {deal_data['notes']}"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_SENDER
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def generate_ai_summary(deal_data):
    prompt = f"""Analyze this real estate deal and give a quick summary and investment insight:
Seller Name: {deal_data['seller_name']}
Property Address: {deal_data['property_address']}
Deal Type: {deal_data['deal_type']}
Notes: {deal_data['notes']}"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()

@app.route('/')
def home():
    return "✅ Deal Offer Pro Backend is Running"

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
    app.run(debug=True)
