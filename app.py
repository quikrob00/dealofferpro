from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Homepage route
@app.route('/')
def home():
    return "✅ Deal Offer Pro is live and ready to submit deals!"

# HTML Deal Submission Form
@app.route('/form')
def form():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deal Offer Pro - Submit Deal</title>
    </head>
    <body>
        <h1>Submit Your Deal</h1>
        <form method="POST" action="/submit-deal">
            <label>Seller Name:</label><br>
            <input type="text" name="seller_name"><br><br>
            <label>Property Address:</label><br>
            <input type="text" name="property_address"><br><br>
            <label>Deal Type:</label><br>
            <select name="deal_type">
                <option value="Cash">Cash</option>
                <option value="Novation">Novation</option>
                <option value="Section 8">Section 8</option>
                <option value="Seller Finance">Seller Finance</option>
            </select><br><br>
            <label>Notes:</label><br>
            <textarea name="notes"></textarea><br><br>
            <button type="submit">Submit Deal</button>
        </form>
    </body>
    </html>
    """)

# Backend POST Route for Form and API Submission
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
    print("✅ Deal Received:", data)
    return jsonify({"message": "Deal submitted successfully!", "data": data}), 200

if __name__ == '__main__':
    app.run(debug=True)
