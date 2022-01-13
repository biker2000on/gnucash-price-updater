import os
from time import sleep

import pandas as pd
import piecash
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange
from datetime import datetime

def price_update(df, commodity, bookdates, currency):
    """
    Add a pandas series and it will add all missing prices since last update.
    """
    total = 0
    for d,v in df.iteritems():
        if d.date() not in bookdates:
            if  (d.date() > bookdates[0]) or (len(bookdates) == 0):
                price = piecash.Price(commodity, currency, d.date(), str("{0:.2f}".format(v)), 'last', 'user:price')
                commodity.prices.append(price)
                total += 1
    return total

def main():
    #Alpha Vantage API Key
    key = os.getenv('ALPHAVANTAGE_API_KEY')

    book = piecash.open_book(uri_conn=os.getenv('DB_URI_CONN'), 
                                open_if_lock=True, 
                                readonly=False, 
                                do_backup=False)

    currency = book.commodities(namespace="CURRENCY", mnemonic="USD")

    for commodity in book.commodities:
        if commodity.quote_flag:
            try:
                name = commodity.mnemonic
                if commodity.namespace == 'EUREX':
                    cc = CryptoCurrencies(key=key, output_format='pandas')
                    data, metadata = cc.get_digital_currency_daily(name, 'USD')
                else:
                    ts = TimeSeries(key=key, output_format='pandas')
                    data, meta_data = ts.get_daily(name, outputsize='compact')
                data.index = pd.to_datetime(data.index)

                bookdates = [price.date for price in commodity.prices]
                bookdates.sort()

                #make a pandas series from the dataframe pulled.
                series = data.loc[:,data.columns.str.contains('close')].iloc[:,0]
                total = price_update(series, commodity, bookdates, currency)
                print(name, commodity.fullname, total, ' added')
            except:
                print('Skipped ' + name + ' due to error in API call.')
            sleep(15)

    book.save()
    book.close()

if __name__ == '__main__':
    main()
