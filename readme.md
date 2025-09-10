# 💵 Banxico USD/MXN Exchange Streamlit App

A **Streamlit** application that queries the **Banxico API** to display:

1. Current FIX exchange rate (USD → MXN).  
2. Average of the last **15 and 30 days**.  
3. Historical values of the last **10 days**.  

The app includes:
- **Optimized API calls** to minimize usage and avoid reaching limits.  
- **Intelligent caching**: short TTL for latest rates (2 min), longer TTL for historical data (10 min).  
- **Rate limit alerts** for both Oportuna and Historica endpoints, including warnings at 50% and 75-85% of limits.  
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
