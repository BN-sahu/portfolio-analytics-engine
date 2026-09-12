Markdown
# 📈 Quant Portfolio Analytics Engine

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

> **Live Demo:** [(https://portfolio-analytics-engine.onrender.com)]

---

## 📖 About This Project

The **Quant Portfolio Analytics Engine** is a production-ready, full-stack web application designed to evaluate, analyze, and optimize financial portfolios. Bridging the gap between rigorous quantitative finance and modern web development, this platform allows users to input custom asset weights or upload portfolio CSVs to instantly generate institutional-grade risk and performance metrics. 

The mathematical backend calculates rolling volatility, Value at Risk (VaR), and uses Ordinary Least Squares (OLS) regression against the S&P 500 to determine asset Beta. Additionally, the application integrates **Modern Portfolio Theory (MPT)**, utilizing SciPy optimization algorithms to calculate the Efficient Frontier and generate optimal asset weights that maximize the Sharpe Ratio or minimize portfolio variance.

The frontend features a responsive, dual-theme (Dark/Light) "Liquid Glassmorphism" UI, delivering complex financial data through sleek, interactive Plotly.js visualizations without ever requiring a page reload.

---

## ✨ Key Features

### 🧮 Quantitative Financial Analytics
* **Market Sensitivity (Beta):** Calculates individual asset beta using `statsmodels` OLS linear regression against benchmark indices.
* **Risk Distribution:** Computes Historical Value at Risk (VaR) at a 95% confidence interval.
* **Modern Portfolio Theory (MPT):** Generates optimized portfolio weights via `scipy.optimize` (SLSQP algorithm) enforcing strict bounds and 100% allocation constraints.
* **Covariance Matrix Mapping:** Accurately computes aggregate portfolio volatility utilizing matrix multiplication (`sqrt(w^T * Cov * w)`).

### 💻 Technical Architecture
* **Decoupled REST API:** Built with Python & Flask, serving clean JSON payloads to the frontend.
* **Secure In-Memory Processing:** Handles user-uploaded CSV files directly in RAM via `io.StringIO` and Pandas, mitigating local filesystem vulnerabilities and path traversal attacks.
* **Asynchronous Rendering:** Utilizes the Fetch API to dynamically update key performance indicators and Plotly charts without full page reloads.
* **Premium UI/UX:** Features a custom CSS Grid layout with an ultra-realistic, frosted liquid glass aesthetic, interactive neon hover states, and seamless Light/Dark mode toggling.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, Gunicorn (WSGI)
* **Data Science & Math:** Pandas, NumPy, SciPy, Statsmodels
* **Market Data:** `yfinance` API
* **Frontend:** HTML5, Vanilla JavaScript, CSS3 (Glassmorphism UI)
* **Data Visualization:** Plotly.js
* **Deployment:** Railway

---

## 📊 Usage Guide

Default View: Upon loading, the dashboard calculates metrics for a default Big Tech portfolio (AAPL, MSFT, GOOGL).

Upload Custom Portfolio: Click "Choose File" to upload a CSV. The CSV must contain Ticker and Weight columns. The backend will parse the data, fetch historical prices, and update the dashboard.

Optimize: In the Optimization Engine panel, select your objective (Max Sharpe or Min Volatility) and click "Generate Efficient Frontier Weights" to see the mathematically optimal allocation for your selected assets.

Theme Toggle: Click the ☀️/🌙 button in the top right to switch between the Dark Neon and Frosted Light glass themes.

## 🔒 Security & Performance Notes

Concurrency: Production deployment utilizes Gunicorn with multiple workers (-w 4) to prevent long-running SciPy mathematical optimizations from blocking concurrent user requests.

Data Privacy: User-uploaded CSV files are processed entirely in memory and immediately discarded. No financial data is written to a database or stored on the server.

Designed & Developed by BN Sahu

## 🚀 Local Setup & Installation

To run this application locally on your machine, follow these steps:

**1. Clone the repository**
```bash
git clone [https://github.com/BN-sahu/portfolio-analytics-engine.git](https://github.com/BN-sahu/portfolio-analytics-engine.git)
cd portfolio-analytics-engine

**2. Create and activate a virtual environment**
```bash
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

**3. Install dependencies**

Bash
pip install -r requirements.txt

**4. Run the development server**

Bash
python app.py

The dashboard will be available at http://127.0.0.1:5000
