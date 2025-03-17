from flask import render_template_string
import markdown

@app.route('/about')
def about():
    with open('README.md', 'r') as f:
        content = f.read()
        html_content = markdown.markdown(content)
    return render_template_string(f'''
        <html>
        <head><title>About Deal Offer Pro</title></head>
        <body>
        <h1>📘 About Deal Offer Pro</h1>
        {html_content}
        </body>
        </html>
    ''')
