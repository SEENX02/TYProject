import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import time  # ✅ Added missing import
import LSTMpredict

# ✅ Improved error handling and retry logic
def getCompanyDetail(companyName, startDate, endDate):
    print(f"Fetching stock data for: {companyName} from {startDate} to {endDate}")  

    for attempt in range(3):  # Retry up to 3 times
        try:
            time.sleep(1)  # ✅ Prevent API rate-limiting
            
            stockData = yf.download(companyName, start=startDate, end=endDate, progress=False, timeout = 3)
            if not stockData.empty:
                print(f"✅ Successfully fetched data for {companyName} on attempt {attempt+1}")
                return pd.DataFrame(stockData)

            print(f"❌ Attempt {attempt+1}: No stock data for {companyName}, retrying...")

        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")

    print(f"🚨 Error: {companyName} still failed after retries.")
    return None

# ✅ Fixed file paths for Render compatibility
def getCandle(companyName, startDate, endDate, theme):
    company = yf.Ticker(companyName)
    print("Searching for company:", companyName)

    data = company.history(start=startDate, end=endDate)

    if data.empty:
        print(f"❌ Invalid company: {companyName}")
        return None  

    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=f'{companyName} Candlestick Chart'
    )])

    fig.update_layout(
        title=f'{companyName} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template=theme
    )

    # ✅ Use relative path for Render compatibility
    file_path = "templates/chart.html"
    fig.write_html(file_path)
    print(f"✅ Candlestick chart saved to {file_path}")

def predict(companyName, startDate, endDate, theme):
    stockData = yf.download(companyName, start=startDate, end=endDate, progress=False)

    if stockData.empty:
        print(f"❌ Invalid company: {companyName}")
        return None  

    # ✅ Proceed with prediction
    return LSTMpredict.predict(companyName, startDate, endDate, theme)
