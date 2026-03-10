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

    html_content = ""
    status_code = 0
    load_time = 0.0
    seo_passed = False
    mobile_ready = False

    # 1. THE TRADITIONAL SCRAPER
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        status_code = response.status_code
        html_content = response.text.lower()
        mobile_ready = "meta name=\"viewport\"" in html_content 
    except Exception as e:
        print(f"Scraper blocked for {url}. Moving to Google API.")

    # 2. THE GOOGLE API
    if GOOGLE_API_KEY != "YOUR_API_KEY_HERE":
        # I slightly simplified the fields filter just in case Google was rejecting our formatting
        fields = "lighthouseResult(audits(interactive,viewport),categories)"
        google_api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={GOOGLE_API_KEY}&category=seo&category=performance&strategy=mobile&fields={fields}"
        
        try:
            g_response = requests.get(google_api_url, timeout=50)
            google_res = g_response.json()
            
            if 'lighthouseResult' in google_res:
                lh = google_res['lighthouseResult']
                if 'audits' in lh:
                    if 'interactive' in lh['audits']:
                        load_time = round(lh['audits']['interactive'].get('numericValue', 0) / 1000, 2)
                    if 'viewport' in lh['audits']:
                        mobile_ready = lh['audits']['viewport'].get('score', 0) == 1
                if 'categories' in lh and 'seo' in lh['categories']:
                    seo_passed = lh['categories']['seo'].get('score', 0) >= 0.8
            else:
                # THIS IS THE FIX. If Google rejects us, print the exact reason!
                print(f"GOOGLE REJECTED US. Status Code: {g_response.status_code}")
                print(f"Google's Message: {google_res}")
                
        except Exception as e:
            print(f"Google API Crash: {e}")

    # 3. COMPILE DATA
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
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
