import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import plotly.graph_objects as go


def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)


def predict(companyName, startDate, endDate, theme):  # Default theme set to 'plotly'
    stockData = yf.download(companyName, start=startDate, end=endDate)
    df1 = stockData[["Close"]].copy()
    df1["Date"] = stockData.index
    scaler = MinMaxScaler(feature_range=(0, 1))
    df1["Close"] = scaler.fit_transform(np.array(df1["Close"]).reshape(-1, 1))

    # Ensure dataset is large enough
    if len(df1) < 75:
        print("Error: Not enough data to create training set.")
        return "Error: Insufficient data for prediction."

    training_size = int(len(df1) * 0.65)
    train_data, test_data = df1["Close"][0:training_size], df1["Close"][training_size:]

    time_step = 75
    X_train, y_train = create_dataset(train_data.values, time_step)
    X_test, y_test = create_dataset(test_data.values, time_step) if len(test_data) > time_step else (np.array([]), np.array([]))

    # Ensure proper input shape before LSTM
    if X_train.size == 0:
        print("Error: X_train is empty. Not enough historical data for training.")
        return "Error: Not enough historical data for training."
    if X_train.ndim == 2:
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    if X_test.size > 0 and X_test.ndim == 2:
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape: {y_test.shape}")

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(time_step, 1)),
        LSTM(50, return_sequences=True),
        LSTM(50),
        Dense(1)
    ])
    model.compile(loss='mean_squared_error', optimizer='adam')

    if X_test.size > 0:
        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=64, verbose=1)
    else:
        model.fit(X_train, y_train, epochs=100, batch_size=64, verbose=1)

    train_predict = scaler.inverse_transform(model.predict(X_train))
    test_predict = scaler.inverse_transform(model.predict(X_test)) if X_test.size > 0 else []

    future_predictions = []
    temp_input = list(test_data[-time_step:].values.flatten()) if len(test_data) >= time_step else list(test_data.values.flatten())
    while len(temp_input) < time_step:
        temp_input.insert(0, 0)
    for i in range(30):
        x_input = np.array(temp_input[-time_step:]).reshape(1, time_step, 1)
        yhat = model.predict(x_input, verbose=0)[0][0]
        future_predictions.append(yhat)
        temp_input.append(yhat)
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1["Date"], y=scaler.inverse_transform(df1[["Close"]]).flatten(), mode='lines', name='Original Data'))
    fig.add_trace(go.Scatter(x=df1["Date"][len(df1) - len(train_predict):], y=train_predict.flatten(), mode='lines', name='Train Predict'))
    if X_test.size > 0:
        fig.add_trace(go.Scatter(x=df1["Date"][len(df1) - len(test_predict):], y=test_predict.flatten(), mode='lines', name='Test Predict'))
    future_dates = [df1["Date"].iloc[-1] + np.timedelta64(i, 'D') for i in range(1, 31)]
    fig.add_trace(go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='1-Month Prediction', line=dict(dash='dot')))
    fig.update_layout(title=f'Stock Price Prediction for {companyName}', xaxis_title='Date', yaxis_title='Stock Price', template=theme)
    fig.show()