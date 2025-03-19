import os
import yfinance as yf  # ✅ Corrected import
from flask import *
import service
import secrets
from flask import sessions
# Suppress TensorFlow debug messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

mySessionKey = secrets.token_hex(16)

# ✅ Flask app setup
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"  # ✅ Ensure session works on Render
Session(app)

@app.route("/")
def interface():
    return render_template("interface.html")

@app.route("/details", methods=["POST", "GET"])
def getPriceHistory():
    companyName = request.form["company"].upper().strip()
    startDate = request.form["startDate"]
    endDate = request.form["endDate"]

    print(f"Received raw ticker: {request.form['company']}")  
    print(f"Processed ticker before appending: {companyName}")  

    if companyName.find(".NS") == -1:
        companyName += ".NS"

    print(f"Final ticker sent to API: {companyName}")

    companyData = service.getCompanyDetail(companyName, startDate, endDate)

    if companyData is None:
        print(f"Error: No data returned for {companyName}")
        return render_template("interface.html", error="Stock data unavailable. Try another ticker.")

    htmlTable = companyData.to_html(classes='table table-striped')
    return render_template("displayTable.html", table=htmlTable)

@app.route("/candle", methods=["POST", "GET"])
def getCandleChart():
    companyName = request.form["company"].upper()
    startDate = request.form["startDate"]
    endDate = request.form["endDate"]
    theme = request.form["theme"]

    if companyName.find(".NS") == -1:
        companyName += ".NS"

    result = service.getCandle(companyName, startDate, endDate, theme)

    if result is None:
        return redirect(url_for("interface", error="Invalid company name. Please try again."))

    return redirect("/")  

app.secret_key = mySessionKey

@app.route("/predict", methods=["POST", "GET"])
def predictor():
    if request.method == "POST":
        session["company"] = request.form["company"]
        session["startDate"] = request.form["startDate"]
        session["endDate"] = request.form["endDate"]
        session["theme"] = request.form["theme"]

    return render_template("warning.html")

@app.route("/processPredict", methods=["POST", "GET"])
def processPredict():
    companyName = session.get("company", "").upper()
    startDate = session.get("startDate", "")
    endDate = session.get("endDate", "")
    theme = session.get("theme", "plotly_dark")

    if companyName.find(".NS") == -1:
        companyName += ".NS"

    try:
        print(f"Predicting for: {companyName}, {startDate} to {endDate}, Theme: {theme}")

        result = service.predict(companyName, startDate, endDate, theme)

        if result is None:
            return redirect(url_for("interface", error="Invalid company name. Please try again."))

    except Exception as e:
        print("Exception occurred:", e)
        return render_template("interface.html", error="An error occurred during prediction. Please try again.")

    return render_template("interface.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Default to 10000
    app.run(host="0.0.0.0", port=port)  # ✅ Removed debug=True for production
