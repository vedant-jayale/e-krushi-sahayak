from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Mapping dictionary for header translations
header_translations = {
    'Sl no.': 'क्र.',
    'Commodity': 'धान्य / फसल',
    'District Name': 'जिल्हा',
    'Market Name': 'बाजार(Market)',
    'Variety': 'प्रकार',
    'Grade': 'गुणवत्ता',
    'Min Price (Rs./Quintal)': 'किमत प्रति क्विंटल(₹) (किमान))',
    'Max Price (Rs./Quintal)': 'किमत प्रति क्विंटल(₹) (कमाल))',
    'Modal Price (Rs./Quintal)': 'सरासरी किमत(₹) (प्रति क्विंटल )',
    'Price Date': 'किमत तारीख'
}

# Function to translate headers
def translate_header(header):
    return header_translations.get(header, header)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

@app.route('/sahayata')
def sahayata():
    return render_template('sahayata.html')

@app.route('/havaman')
def havaman():
    return render_template('havaman.html')

@app.route('/kapusvyavasthapan')
def kapusvyavasthapan():
    return render_template('kapusvyavasthapan.html')

@app.route('/soil-testing')
def soiltesting():
    return render_template('soil-testing.html')

@app.route('/get_prices', methods=['GET', 'POST'])
def get_prices():
    data = None
    form_submitted = False
    if request.method == 'POST':
        form_submitted = True
        commodity = request.form['commodity']
        state = request.form['state']
        district = request.form['district']
        market = request.form['market']
        date_from = request.form['date_from']
        date_to = request.form['date_to']

        commodity_name = request.form['commodity_name']
        state_name = request.form['state_name']
        district_name = request.form['district_name']
        market_name = request.form['market_name']

        url = (f"https://agmarknet.gov.in/SearchCmmMkt.aspx?"
               f"Tx_Commodity={commodity}&Tx_State={state}&Tx_District={district}&Tx_Market={market}"
               f"&DateFrom={date_from}&DateTo={date_to}&Fr_Date={date_from}&To_Date={date_to}&Tx_Trend=0"
               f"&Tx_CommodityHead={commodity_name}&Tx_StateHead={state_name}&Tx_DistrictHead={district_name}&Tx_MarketHead={market_name}")

        # Scraper API setup
        scraper_api_url = "https://api.scraperapi.com"
        api_key = "abbd392168a5681912e35e5698f9db14"  # Your Scraper API key
        params = {
            'api_key': api_key,
            'url': url  # The Agmarknet URL you want to scrape
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://agmarknet.gov.in",
            "Connection": "keep-alive"
        }

        try:
            # Send request through Scraper API
            response = requests.get(scraper_api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data (adjust selectors as needed)
                table = soup.find('table', {'class': 'tableagmark_new'})  # Adjust class name based on the actual table
                if table:
                    headers = [translate_header(th.text.strip()) for th in table.find_all('th')]
                    rows = []
                    for row in table.find_all('tr')[1:]:
                        cols = [col.text.strip() for col in row.find_all('td')]
                        if 'No Data Found' in cols:
                            data = None
                            break
                        rows.append(dict(zip(headers, cols)))
                    data = {'headers': headers, 'rows': rows}
                else:
                    data = None
            else:
                data = None
        except requests.exceptions.RequestException as e:
            print(f"Error during requests: {e}")
            data = None

    return render_template('index.html', data=data, form_submitted=form_submitted)

if __name__ == '__main__':
    app.run(debug=True)
