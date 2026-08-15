let currentTickers = ['AAPL', 'MSFT', 'GOOGL'];
let currentWeights = [0.4, 0.3, 0.3];
let isLightMode = false;

// Theme Toggle Function
function toggleTheme() {
    isLightMode = !isLightMode;
    document.body.classList.toggle('light-theme', isLightMode);
    
    // Update button text
    const btn = document.getElementById('theme-toggle');
    btn.innerText = isLightMode ? '🌙 Dark Mode' : '☀️ Light Mode';
    
    // If charts exist, dynamically update their font colors without reloading data
    if (document.getElementById('allocation-chart').data) {
        const newFontColor = isLightMode ? '#0f172a' : '#f8fafc';
        Plotly.relayout('allocation-chart', { font: { color: newFontColor } });
        Plotly.relayout('risk-return-chart', { font: { color: newFontColor } });
    }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    analyze(currentTickers, currentWeights);
});

async function analyze(tickers, weights) {
    try {
        const response = await fetch('/api/portfolio/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickers, weights })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        updateUI(data);
    } catch (error) {
        alert("Analysis Error: " + error.message);
    }
}

function updateUI(data) {
    // Update KPIs
    const formatPct = (val) => (val * 100).toFixed(2) + '%';
    document.getElementById('kpi-return').innerText = formatPct(data.portfolio.annual_return);
    document.getElementById('kpi-volatility').innerText = formatPct(data.portfolio.volatility);
    document.getElementById('kpi-sharpe').innerText = data.portfolio.sharpe_ratio.toFixed(2);

    // Update Table
    const tbody = document.querySelector('#holdings-table tbody');
    tbody.innerHTML = '';
    
    let tickerLabels = [];
    let secReturns = [];
    let secVols = [];

    data.securities.forEach(sec => {
        tickerLabels.push(sec.ticker);
        secReturns.push(sec.annual_return);
        secVols.push(sec.volatility);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${sec.ticker}</strong></td>
            <td>${formatPct(sec.weight)}</td>
            <td>${formatPct(sec.annual_return)}</td>
            <td>${formatPct(sec.volatility)}</td>
            <td>${sec.beta.toFixed(2)}</td>
            <td style="color: var(--negative)">${formatPct(sec.var_95)}</td>
        `;
        tbody.appendChild(tr);
    });

    // Determine font color based on current theme
    const chartFontColor = isLightMode ? '#0f172a' : '#f8fafc';

    // Render Allocation Donut Chart
    Plotly.newPlot('allocation-chart', [{
        values: currentWeights,
        labels: tickerLabels,
        type: 'pie',
        hole: 0.4,
        marker: { colors: ['#3b82f6', '#10b981', '#6366f1', '#f59e0b', '#8b5cf6'] }
    }], {
        title: 'Current Asset Allocation',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { color: chartFontColor }
    });

    // Render Risk/Return Scatter
    Plotly.newPlot('risk-return-chart', [{
        x: secVols,
        y: secReturns,
        mode: 'markers+text',
        type: 'scatter',
        text: tickerLabels,
        textposition: 'top center',
        marker: { size: 12, color: '#3b82f6' }
    }], {
        title: 'Risk vs. Return (Individual Assets)',
        xaxis: { title: 'Volatility (Risk)' },
        yaxis: { title: 'Annual Return' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: chartFontColor }
    });
}

async function uploadPortfolio() {
    const fileInput = document.getElementById('csv-upload');
    if (!fileInput.files.length) return alert("Select a CSV file first.");

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/api/portfolio/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentTickers = data.tickers;
        currentWeights = data.weights;
        analyze(currentTickers, currentWeights);
    } catch (error) {
        alert("Upload Error: " + error.message);
    }
}

async function optimizePortfolio() {
    const objective = document.getElementById('opt-objective').value;
    try {
        const response = await fetch('/api/portfolio/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickers: currentTickers, objective: objective })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        let resultHTML = '<strong>Optimized Weights:</strong><br>';
        for (const [ticker, weight] of Object.entries(data.optimized_weights)) {
            resultHTML += `${ticker}: ${(weight * 100).toFixed(2)}% | `;
        }
        document.getElementById('opt-results').innerHTML = resultHTML;
    } catch (error) {
        alert("Optimization Error: " + error.message);
    }
}