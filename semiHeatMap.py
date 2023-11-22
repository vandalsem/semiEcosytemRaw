from flask import Flask, render_template
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello_world():
    companies = get_data()
    columns = 'Symbol,Name,Ctry,Primary Chip,Market Cap,Total Return (YTD),Revenues (LTM),FCF (LTM),FCF/Share (LTM),PEG (NTM),P/E (LTM),Fwd P/E (NTM)'.split(',')
    return render_template('index.html', companies=companies,columns=columns)

# Helpers
def get_data():
    companies = pd.read_csv('data/subsector_semis.csv',keep_default_na=False)
    company_data = pd.read_csv('data/comp_daily_update.csv',keep_default_na=False)

    company_data = company_data.drop(columns='Name,Last Price,1-Day %,Beta (2Y),Revenues - Est Avg (NTM),FCF - Est Avg (FY1E),Country,Next Earnings (When),Net EPS - Diluted (LTM),Next Earnings (When)'.split(','))

    companies = companies.merge(company_data,how='left',on='Ticker')
    
    companies['yahooLink'] = np.where(companies['yahooLink']=='',f'https://finance.yahoo.com/quote/'+companies['Ticker'],companies['yahooLink'])
    
    sortMap = ['Design','IDM','EDA','IP','Fabrication','Equipment','Materials','TPA']

    companies['FCF (LTM)'] = np.where(companies['FCF (LTM)']=='', 0, companies['FCF (LTM)'])
    companies['FCF (LTM)'] = companies['FCF (LTM)'].astype(float)

    companies.subSector = pd.Categorical(companies.subSector,categories=sortMap,ordered=True)
    companies.sort_values(by=['subSector','Market Cap'],ascending=[True,False],inplace=True)

    companies['ISO Earnings'] = pd.to_datetime(companies['Next Earnings (Date)']).dt.strftime('%Y%m%d')

    companies = companies.to_dict('records')
    return companies

if __name__ == '__main__':
    app.run(debug=True)