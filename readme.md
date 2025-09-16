# 💵 Banxico USD/MXN Exchange Streamlit App


A **Streamlit** application that queries the **Banxico API** to display:

1. Current FIX exchange rate (USD → MXN).  
2. Average of the last **15 and 30 days**.  
3. Historical values of the last **10 days**.  

The app includes:
- **Optimized API calls** to minimize usage and avoid reaching limits.  
- **Intelligent caching**: short TTL for latest rates (2 min), longer TTL for historical data (10 min).  
- **Rate limit alerts** for both Oportuna and Historica endpoints, including warnings at 50% and 75-85% of limits.  
- **Dark theme card UI** with responsive design.  
- **Result caching** for performance improvements.  

---

## ⚡ Requirements

- Python 3.10+ (if running locally without Docker).  
- A valid **Banxico token** → obtainable from Banxico’s developer portal.  

---

## 🚀 Local Installation (without Docker)

```bash
# Clone the repository
git clone https://github.com/your_username/banxico-app.git
cd banxico-app

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Export the token
export BANXICO_TOKEN=your_token_here

# Run the app
streamlit run app.py
```

The app will be available at 👉 [http://localhost:8501](http://localhost:8501).  

---

## 🐳 Run with Docker Compose

### 1. Configure the token
Create a **.env** file in the project root:  
```env
BANXICO_TOKEN=your_token_here
```

### 2. Start the container
```bash
docker-compose up --build
```

Open in 👉 [http://localhost:8501](http://localhost:8501).  

---

## 🔄 GitHub Actions Pipeline

This repo includes a workflow in `.github/workflows/build.yml` that:  
- Builds the Docker image in GitHub Actions on every push to `main`.  
- Validates the `Dockerfile`.  

> ⚠️ The image is **not pushed to any registry**: deployment is handled locally with `docker-compose`.  

---

## 🛠️ Main Functions

- **`fetch_oportuna_fix()`** → Fetches the most recent FIX exchange rate (USD→MXN).  
- **`fetch_historica_fix(start, end)`** → Retrieves historical exchange rates in a single call to cover all calculations.  
- **`avg_last_n_points(df, n)`** → Computes the average of the last `n` data points.  
- **`check_rate_alerts(kind)`** → Alerts when API requests reach 50%, 75%, or daily thresholds.  
- **Optimized caching** → Avoids repeated API calls while keeping data up-to-date.  

---

## 📊 API Usage & Estimated Daily Calls

| Data Requested           | Endpoint   | Calls per refresh | Refreshes/day (15 min) | Total calls/day |
|--------------------------|------------|-----------------|-----------------------|----------------|
| Current USD→MXN FIX      | Oportuna   | 1               | 96                    | 96             |
| Historical last 120 days | Historica  | 1               | 96                    | 96             |

> Total daily calls = 192, safely below Banxico's daily limits (Oportuna: 40,000, Historica: 10,000).  

---

## 📊 UI Example

The app displays modern cards showing:  
- Current FIX rate (USD → MXN).  
- Averages for the last 15 and 30 days.  
- Last 10 historical records.  

---

## 📜 License

MIT License © 2025
