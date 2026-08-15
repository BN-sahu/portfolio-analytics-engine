import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.stats import norm

TRADING_DAYS = 252

def fetch_market_data(tickers, period="2y"):
    """Fetches historical adjusted close prices."""
    try:
        data = yf.download(tickers, period=period)
        
        # Handle MultiIndex columns returned by newer yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            if 'Adj Close' in data.columns.levels[0]:
                data = data['Adj Close']
            elif 'Close' in data.columns.levels[0]:
                data = data['Close']
        elif 'Adj Close' in data.columns:
            data = data['Adj Close']
        elif 'Close' in data.columns:
            data = data['Close']

        # Ensure single ticker returns a DataFrame, not a Series
        if isinstance(data, pd.Series):
            data = data.to_frame()

        return data.dropna()
    except Exception as e:
        print(f"Market Data Error: {e}")
        return pd.DataFrame()

def analyze_portfolio(data, tickers, weights, benchmark):
    """Calculates security metrics, regression (Beta), and portfolio aggregates."""
    returns = data.pct_change().dropna()
    
    port_metrics = {}
    sec_metrics = []
    
    bench_returns = returns[benchmark] if benchmark in returns.columns else None

    # Individual Security Analysis
    for i, ticker in enumerate(tickers):
        sec_ret = returns[ticker]
        mean_ret = sec_ret.mean() * TRADING_DAYS
        volatility = sec_ret.std() * np.sqrt(TRADING_DAYS)
        
        # Historical VaR (95% confidence)
        var_95 = np.percentile(sec_ret, 5)
        
        # Market Sensitivity (OLS Regression)
        beta, alpha, r_squared = 1.0, 0.0, 0.0
        if bench_returns is not None:
            X = sm.add_constant(bench_returns)
            model = sm.OLS(sec_ret, X).fit()
            alpha, beta = model.params
            r_squared = model.rsquared
            
        sec_metrics.append({
            'ticker': ticker,
            'weight': weights[i],
            'annual_return': mean_ret,
            'volatility': volatility,
            'beta': beta,
            'alpha': alpha * TRADING_DAYS,
            'r_squared': r_squared,
            'var_95': var_95
        })

    # Portfolio Level Analysis
    weight_arr = np.array(weights)
    cov_matrix = returns[tickers].cov() * TRADING_DAYS
    
    port_return = np.sum(returns[tickers].mean() * weight_arr) * TRADING_DAYS
    port_volatility = np.sqrt(np.dot(weight_arr.T, np.dot(cov_matrix, weight_arr)))
    
    sharpe_ratio = port_return / port_volatility if port_volatility > 0 else 0

    return {
        'portfolio': {
            'annual_return': port_return,
            'volatility': port_volatility,
            'sharpe_ratio': sharpe_ratio
        },
        'securities': sec_metrics,
        'correlation': returns[tickers].corr().to_dict()
    }

def optimize_portfolio(data, tickers, objective='sharpe'):
    """Generates the Markowitz Efficient Frontier optimal weights."""
    returns = data[tickers].pct_change().dropna()
    mean_returns = returns.mean() * TRADING_DAYS
    cov_matrix = returns.cov() * TRADING_DAYS
    num_assets = len(tickers)
    
    args = (mean_returns, cov_matrix)
    
    # Objective Functions
    def neg_sharpe(weights, mean_returns, cov_matrix, risk_free_rate=0.0):
        p_ret = np.sum(mean_returns * weights)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(p_ret - risk_free_rate) / p_vol
        
    def min_volatility(weights, mean_returns, cov_matrix):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    # Constraints: Weights sum exactly to 100% (1.0), long-only (0 to 1)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    
    initial_guess = num_assets * [1. / num_assets,]
    
    if objective == 'sharpe':
        result = minimize(neg_sharpe, initial_guess, args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    else:
        result = minimize(min_volatility, initial_guess, args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
                        
    optimized_weights = np.round(result.x, 4)
    
    return {
        'optimized_weights': dict(zip(tickers, optimized_weights)),
        'success': result.success,
        'message': result.message
    }