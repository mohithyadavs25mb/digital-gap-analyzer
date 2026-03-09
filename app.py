from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def scan_website():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        start_time = time.time()
        # Added headers to pretend we are a real browser, helps prevent getting blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        load_time = round(time.time() - start_time, 2)
        
        html_content = response.text.lower()
        
        # UPGRADED DATA DICTIONARY
        result = {
            "url": url,
            "status_code": response.status_code,
            "load_time_seconds": load_time,
            "ssl_secure": url.startswith('https'),
            "seo_present": "<title>" in html_content and "meta name=\"description\"" in html_content,
            "mobile_ready": "meta name=\"viewport\"" in html_content,
            
            # --- NEW VARIABLES ---
            "has_analytics": "google-analytics" in html_content or "gtag(" in html_content,
            "has_socials": "linkedin.com" in html_content or "twitter.com" in html_content or "facebook.com" in html_content,
            "is_wordpress": "wp-content" in html_content or "wp-includes" in html_content,
            "has_contact_email": "mailto:" in html_content
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": "Failed to scan. Website might be down or blocking bots.", "url": url}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
