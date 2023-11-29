from flask import Flask, render_template
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

@app.route('/')
def index():
    companies = get_data()
    sox_quote = get_sox()
    columns = 'Symbol,Name,Ctry,Primary Chip,Market Cap,Total Return (YTD),Revenues (LTM),EV/Revenue (LTM),FCF (LTM),FCF/Share (LTM),P/E (LTM),PEG (NTM)'.split(',')
    return render_template('index.html', companies=companies,columns=columns,sox_quote=sox_quote)

# Helpers
def get_data():
    companies = pd.read_csv('data/subsector_semis.csv',keep_default_na=False)
    company_data = pd.read_csv('data/comp_daily_update.csv',keep_default_na=False)

    company_data = company_data.drop(columns='Name,Last Price,1-Day %,Revenues - Est Avg (NTM),FCF - Est Avg (FY1E),Country,Next Earnings (When),Net EPS - Diluted (LTM),Next Earnings (When)'.split(','))

    companies = companies.merge(company_data,how='left',on='Ticker')
    
    companies['yahooLink'] = np.where(companies['yahooLink']=='',f'https://finance.yahoo.com/quote/'+companies['Ticker'],companies['yahooLink'])
    
    sortMap = ['Design','IDM','EDA','IP','Fabrication','Equipment','Materials','TPA']

    companies['FCF (LTM)'] = np.where(companies['FCF (LTM)']=='', 0, companies['FCF (LTM)'])
    companies['FCF (LTM)'] = companies['FCF (LTM)'].astype(float)

    companies.subSector = pd.Categorical(companies.subSector,categories=sortMap,ordered=True)
    companies.sort_values(by=['subSector','Market Cap'],ascending=[True,False],inplace=True)

    companies['ISO Earnings'] = pd.to_datetime(companies['Next Earnings (Date)']).dt.strftime('%Y%m%d')

    def total_return(row):
        return '' if row['Total Return (YTD)'] == '' else round((float(row['Total Return (YTD)'])*100),2)
    
    companies['Total Return (YTD)'] = companies.apply(total_return,axis=1)

    companies = companies.to_dict('records')
    return companies

def get_sox():
    page = requests.get("https://finance.yahoo.com/quote/%5ESOX?p=^SOX&.tsrc=fin-srch",headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs(page.text,'html.parser')
    quote = soup.find_all("div", {"class": "D(ib) Mend(20px)"})
    price = quote[0].find('fin-streamer').get("value")
    prince_change = quote[0].find_all('span')[0].text
    perc_change = quote[0].find_all('span')[1].text[1:-1]
    return [price,prince_change,perc_change]

if __name__ == '__main__':
    app.run(debug=True)