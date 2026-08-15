import os
import io
import pandas as pd
from flask import Flask, request, jsonify, render_template
from services.analytics import fetch_market_data, analyze_portfolio, optimize_portfolio

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/portfolio/analyze', methods=['POST'])
def api_analyze_portfolio():
    try:
        data = request.json
        tickers = data.get('tickers', [])
        weights = data.get('weights', [])
        benchmark = data.get('benchmark', '^GSPC') # Default S&P 500

        if not tickers or len(tickers) != len(weights):
            return jsonify({'error': 'Invalid tickers or weights length mismatch.'}), 400
        
        # Normalize weights to exactly 1.0 (100%)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Fetch Data
        market_data = fetch_market_data(tickers + [benchmark])
        if market_data.empty:
            return jsonify({'error': 'Failed to fetch market data.'}), 500

        # Run Analysis
        metrics = analyze_portfolio(market_data, tickers, weights, benchmark)
        return jsonify(metrics)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/optimize', methods=['POST'])
def api_optimize_portfolio():
    try:
        data = request.json
        tickers = data.get('tickers', [])
        objective = data.get('objective', 'sharpe') # 'sharpe' or 'volatility'

        if len(tickers) < 2:
            return jsonify({'error': 'Optimization requires at least 2 assets.'}), 400

        market_data = fetch_market_data(tickers)
        opt_results = optimize_portfolio(market_data, tickers, objective)
        
        return jsonify(opt_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/upload', methods=['POST'])
def api_upload_portfolio():
    # Secure in-memory file processing (no local filesystem writes)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part provided.'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file. Must be CSV.'}), 400

    try:
        # Read directly from the file stream into pandas
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df = pd.read_csv(stream)
        
        required_cols = {'Ticker', 'Weight'}
        if not required_cols.issubset(set(df.columns)):
            return jsonify({'error': 'CSV must contain "Ticker" and "Weight" columns.'}), 400
        
        # Clean and validate
        df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
        df = df.dropna(subset=['Ticker', 'Weight'])
        
        return jsonify({
            'tickers': df['Ticker'].tolist(),
            'weights': df['Weight'].tolist()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to process CSV: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)