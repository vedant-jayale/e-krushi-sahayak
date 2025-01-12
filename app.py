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

        headers = {
            
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://agmarknet.gov.in",
            "Connection": "keep-alive"

        }

        try:
            # Test connection to the site
            test_response = requests.get('https://www.agmarknet.gov.in', timeout=10)
            if test_response.status_code != 200:
                print(f"Error: Unable to connect to Agmarknet. Status Code: {test_response.status_code}")
                return render_template('error.html', message="Unable to connect to Agmarknet website.")
            
            # Fetch market data
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data (adjust selectors as needed)
                table = soup.find('table', {'class': 'table-class'})  # Replace 'table-class' with actual class name
                if table:
                    headers = [translate_header(th.text.strip()) for th in table.find_all('th')]
                    rows = []
                    for row in table.find_all('tr')[1:]:
                        cols = [col.text.strip() for col in row.find_all('td')]
                        rows.append(cols)
                    data = {'headers': headers, 'rows': rows}
                else:
                    print("No table found in the response.")
            else:
                print(f"Error fetching data. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error during requests to Agmarknet: {e}")
            return render_template('error.html', message="An error occurred while fetching data.")

    return render_template('get_prices.html', data=data, form_submitted=form_submitted)



if __name__ == '__main__':
    app.run(debug=True)
