from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
# This allows your frontend website to talk to this backend
CORS(app)

@app.route('/scan', methods=['POST'])
def scan_website():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    # Ensure URL is formatted correctly
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        # Start the timer and visit the website
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = round(time.time() - start_time, 2)
        
        # Analyze the website's code for our MBA project variables
        html_content = response.text.lower()
        
        result = {
            "url": url,
            "status_code": response.status_code,
            "load_time_seconds": load_time,
            "ssl_secure": url.startswith('https'),
            "seo_present": "<title>" in html_content and "meta name=\"description\"" in html_content,
            "mobile_ready": "meta name=\"viewport\"" in html_content
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": "Failed to scan. Website might be down or blocking bots.", "url": url}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
