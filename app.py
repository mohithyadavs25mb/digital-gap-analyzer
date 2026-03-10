from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# --- PASTE YOUR GOOGLE API KEY INSIDE THE QUOTES BELOW ---
GOOGLE_API_KEY = "AIzaSyD74FeGZVHd_Bdjd6zNWZvQx3Hw3NP5Zrg"

@app.route('/scan', methods=['POST'])
def scan_website():
    data = request.json
    url = data.get('url')
    
    if not url: return jsonify({"error": "No URL provided"}), 400
    if not url.startswith('http'): url = 'https://' + url

    html_content = ""
    status_code = 0
    seo_passed = False
    mobile_ready = False
    
    # DIAGNOSTIC BASELINE
    load_time = 555.55

    # 1. THE TRADITIONAL SCRAPER
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        html_content = response.text.lower()
    except:
        pass # Ignore scraper errors for this diagnostic test

    # 2. THE DIAGNOSTIC GOOGLE API
    if GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        load_time = 777.77 # SECRET CODE: Key is missing or unreadable
    else:
        # I removed the fields filter temporarily just in case Google was rejecting the format
        google_api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={GOOGLE_API_KEY}&category=seo&category=performance&strategy=mobile"
        
        try:
            g_res = requests.get(google_api_url, timeout=40)
            
            if g_res.status_code != 200:
                # SECRET CODE: Google rejected us. Print their exact HTTP error code to the screen!
                load_time = float(g_res.status_code) 
            else:
                json_data = g_res.json()
                if 'lighthouseResult' in json_data:
                    lh = json_data['lighthouseResult']
                    load_time = round(lh['audits']['interactive'].get('numericValue', 0) / 1000, 2)
                    seo_passed = lh['categories']['seo'].get('score', 0) >= 0.8
                    mobile_ready = lh['audits']['viewport'].get('score', 0) == 1
                else:
                    load_time = 888.88 # SECRET CODE: Data format changed
        except Exception as e:
            load_time = 999.99 # SECRET CODE: Server crashed trying to connect

    # 3. COMPILE DATA
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
        "has_sales_automation": "tawk.to" in html_content or "intercom" in html_content or "zendesk" in html_content,
        "has_mobile_apps": "play.google.com" in html_content or "apps.apple.com" in html_content
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
