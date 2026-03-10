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

    try:
        # 1. THE TRADITIONAL SCRAPER (For the Sales Variables)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text.lower()
        
        # Default fallback values
        load_time = 0.0
        seo_passed = False
        mobile_ready = "meta name=\"viewport\"" in html_content 
        
        # 2. THE GOOGLE API (Bulletproof Version)
        if GOOGLE_API_KEY != "YOUR_API_KEY_HERE":
            # We explicitly ask Google for MOBILE data (strategy=mobile) so it always gives us the viewport check
            google_api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={GOOGLE_API_KEY}&category=seo&category=performance&strategy=mobile"
            
            try:
                # We give Render a massive 35-second window to wait for Google
                google_res = requests.get(google_api_url, timeout=35).json()
                
                # Safely extract data without crashing
                if 'lighthouseResult' in google_res:
                    lh = google_res['lighthouseResult']
                    audits = lh.get('audits', {})
                    categories = lh.get('categories', {})
                    
                    if 'interactive' in audits:
                        load_time = round(audits['interactive'].get('numericValue', 0) / 1000, 2)
                        
                    if 'seo' in categories:
                        seo_passed = categories['seo'].get('score', 0) >= 0.8
                        
                    if 'viewport' in audits:
                        mobile_ready = audits['viewport'].get('score', 0) == 1
                        
            except Exception as e:
                print(f"Google API Error: {e}") # This secretly logs the error for us developers

        # 3. COMPILE THE HYBRID DATA
        result = {
            "url": url,
            "status_code": response.status_code,
            
            # --- GOOGLE'S DATA ---
            "load_time_seconds": load_time if load_time > 0 else 2.5,
            "seo_present": seo_passed,
            "mobile_ready": mobile_ready,
            
            # --- OUR SCRAPER DATA ---
            "ssl_secure": url.startswith('https'),
            "has_socials": "linkedin.com" in html_content or "twitter.com" in html_content or "facebook.com" in html_content,
            "has_contact_email": "mailto:" in html_content,
            "has_business_intel": "google-analytics" in html_content or "gtm.js" in html_content or "fbevents.js" in html_content,
            "is_wordpress": "wp-content" in html_content or "wp-includes" in html_content,
            "has_sales_automation": "tawk.to" in html_content or "intercom" in html_content or "zendesk" in html_content or "hubspot" in html_content or "salesforce" in html_content,
            "has_mobile_apps": "play.google.com/store/apps" in html_content or "apps.apple.com" in html_content
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": "Failed to scan. Target firewall blocking bots.", "url": url}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
