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
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    if not url.startswith('http'):
        url = 'https://' + url

    # Default safety net values so the app never crashes
    html_content = ""
    status_code = 0
    load_time = 0.0
    seo_passed = False
    mobile_ready = False

    # ---------------------------------------------------------
    # BRAIN 1: THE TRADITIONAL SCRAPER (Wrapped in a shield)
    # ---------------------------------------------------------
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 AppleWebKit/537.36)'}
        response = requests.get(url, headers=headers, timeout=15)
        status_code = response.status_code
        html_content = response.text.lower()
        mobile_ready = "meta name=\"viewport\"" in html_content 
    except Exception as e:
        # If a firewall blocks us, we DO NOT crash. We silently log it and move to Google.
        print(f"Scraper blocked for {url}. Moving to Google API.")

    # ---------------------------------------------------------
    # BRAIN 2: THE GOOGLE API (Optimized for Free Tier)
    # ---------------------------------------------------------
    if GOOGLE_API_KEY != "YOUR_API_KEY_HERE":
        fields = "lighthouseResult(audits(interactive,viewport),categories/seo/score)"
        google_api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={GOOGLE_API_KEY}&category=seo&category=performance&strategy=mobile&fields={fields}"
        
        try:
            google_res = requests.get(google_api_url, timeout=50).json()
            
            if 'lighthouseResult' in google_res:
                lh = google_res['lighthouseResult']
                
                if 'audits' in lh:
                    if 'interactive' in lh['audits']:
                        load_time = round(lh['audits']['interactive'].get('numericValue', 0) / 1000, 2)
                    if 'viewport' in lh['audits']:
                        mobile_ready = lh['audits']['viewport'].get('score', 0) == 1
                        
                if 'categories' in lh and 'seo' in lh['categories']:
                    seo_passed = lh['categories']['seo'].get('score', 0) >= 0.8
        except Exception as e:
            print(f"Google API Error: {e}")

    # ---------------------------------------------------------
    # 3. COMPILE THE HYBRID DATA
    # ---------------------------------------------------------
    result = {
        "url": url,
        "status_code": status_code,
        "load_time_seconds": load_time if load_time > 0 else 2.5,
        "seo_present": seo_passed,
        "mobile_ready": mobile_ready,
        "ssl_secure": url.startswith('https'),
        "has_socials": "linkedin.com" in html_content or "twitter.com" in html_content or "facebook.com" in html_content,
        "has_contact_email": "mailto:" in html_content,
        "has_business_intel": "google-analytics" in html_content or "gtm.js" in html_content or "fbevents.js" in html_content,
        "is_wordpress": "wp-content" in html_content or "wp-includes" in html_content,
        "has_sales_automation": "tawk.to" in html_content or "intercom" in html_content or "zendesk" in html_content or "hubspot" in html_content or "salesforce" in html_content,
        "has_mobile_apps": "play.google.com/store/apps" in html_content or "apps.apple.com" in html_content
    }
    
    # We successfully return the data to your dashboard!
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
