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
    
    if not url: return jsonify({"error": "No URL provided"}), 400
    if not url.startswith('http'): url = 'https://' + url

    html_content = ""
    status_code = 0
    load_time = 0.0
    seo_passed = False
    mobile_ready = False
    
    try:
        # START THE STOPWATCH
        start_time = time.time()
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 AppleWebKit/537.36)'}
        response = requests.get(url, headers=headers, timeout=15)
        
        # STOP THE STOPWATCH
        end_time = time.time()
        
        # Calculate exact load time
        load_time = round(end_time - start_time, 2)
        status_code = response.status_code
        html_content = response.text.lower()
        
        # NATIVE SEO & MOBILE CHECK (We look for the exact code tags ourselves)
        seo_passed = "<title" in html_content and "meta name=\"description\"" in html_content
        mobile_ready = "meta name=\"viewport\"" in html_content 

    except Exception as e:
        # If the site is completely dead or blocks us
        status_code = 404
        load_time = 0.0

    # COMPILE DATA
    result = {
        "url": url,
        "status_code": status_code,
        "load_time_seconds": load_time,
        "seo_present": seo_passed,
        "mobile_ready": mobile_ready,
        "ssl_secure": url.startswith('https'),
        "has_socials": "linkedin.com" in html_content or "twitter.com" in html_content or "facebook.com" in html_content,
        "has_contact_email": "mailto:" in html_content,
        "has_business_intel": "google-analytics" in html_content or "gtm.js" in html_content or "fbevents.js" in html_content,
        "is_wordpress": "wp-content" in html_content or "wp-includes" in html_content,
        "has_sales_automation": "tawk.to" in html_content or "intercom" in html_content or "zendesk" in html_content or "hubspot" in html_content,
        "has_mobile_apps": "play.google.com" in html_content or "apps.apple.com" in html_content
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
