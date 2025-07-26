from flask import Flask, request, redirect
import mysql.connector
import hashlib

app = Flask(__name__)

# MySQL config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nam1234',
    'database': 'test'
}

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = ""
    clicks = None

    if request.method == 'POST':
        long_url = request.form['long_url']

        # Generate a short key
        short_key = hashlib.md5(long_url.encode()).hexdigest()[:6]

        # Store or fetch from MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if URL already exists
        cursor.execute("SELECT short_key, clicks FROM urls WHERE long_url = %s", (long_url,))
        existing = cursor.fetchone()
        if existing:
            short_key, clicks = existing
        else:
            cursor.execute("INSERT INTO urls (long_url, short_key) VALUES (%s, %s)", (long_url, short_key))
            conn.commit()
            clicks = 0  # newly created

        cursor.close()
        conn.close()

        short_url = request.host_url + short_key

    # HTML response
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>URL Shortener</title>
    <style>
        body {{
            font-family: Arial;
            background: linear-gradient(to right, #667eea, #764ba2);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            text-align: center;
            width: 400px;
        }}
        input[type="text"], button {{
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }}
        button {{
            background-color: #5a67d8;
            color: white;
            border: none;
            font-weight: bold;
        }}
        a {{
            color: #5a67d8;
            font-weight: bold;
        }}
        .result {{
            margin-top: 15px;
            background: #f0f4ff;
            padding: 10px;
            border-radius: 6px;
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <h2>URL Shortener</h2>
        <form method="POST">
            <input type="text" name="long_url" placeholder="Enter your long URL" required>
            <button type="submit">Shorten</button>
        </form>
        {f"<div class='result'>Shortened URL: <a href='{short_url}' target='_blank'>{short_url}</a><br>Clicks: {clicks}</div>" if short_url else ""}
    </div>
    </body>
    </html>
    '''


@app.route('/<short_key>')
def redirect_to_long_url(short_key):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get long URL
    cursor.execute("SELECT long_url FROM urls WHERE short_key = %s", (short_key,))
    result = cursor.fetchone()

    if result:
        long_url = result[0]

        # Increment clicks
        cursor.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_key = %s", (short_key,))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(long_url)
    else:
        cursor.close()
        conn.close()
        return "URL not found", 404


if __name__ == '__main__':
    app.run(debug=True)
