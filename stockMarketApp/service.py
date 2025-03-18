import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import webbrowser
import LSTMpredict


def getCompanyDetail(companyName, startDate, endDate):
    # Fetch the stock data
    stockData = yf.download(companyName, start=startDate, end=endDate)

    df = pd.DataFrame(stockData)
    return df

def getCandle(companyName, startDate, endDate, theme):
    company = yf.Ticker(companyName)
    print("Searching for company:", companyName)

    data = company.history(start=startDate, end=endDate)

    # Check if the company is invalid (empty data)
    if data.empty:
        print(f"Invalid company: {companyName}")
        return None  # Return None to indicate failure

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

    file_path = "C:/College Notes/Sem6/Project/stockMarketApp/templates/chart.html"
    fig.write_html(file_path)
    # Automatically open in Microsoft Edge
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.get('edge').open(file_path)

def predict(companyName, startDate, endDate, theme):
    stockData = yf.download(companyName, start=startDate, end=endDate)

    # Check if the company is invalid (empty data)
    if stockData.empty:
        print(f"Invalid company: {companyName}")
        return None  # Return None to indicate failure

    # Proceed with prediction
    return LSTMpredict.predict(companyName, startDate, endDate, theme)
