"""
Bio Farma Procurement Assistant - Flask Application
Single file with API endpoints and HTML interface
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template_string, request, jsonify
import pandas as pd
from src.agent import ProcurementAgent
from use_cases.create_po import POCreator
from use_cases.validate_invoice import InvoiceValidator
from use_cases.price_comparison import PriceComparator

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'biofarma-procurement-2024'

# Initialize components
try:
    agent = ProcurementAgent()
    agent_loaded = True
except Exception as e:
    agent = None
    agent_loaded = False
    print(f"⚠️  Warning: Agent failed to load: {str(e)}")

po_creator = POCreator()
invoice_validator = InvoiceValidator()
price_comparator = PriceComparator()

# HTML Template (embedded in same file)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bio Farma Procurement Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab {
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 1em;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        
        .tab:hover {
            background: #e8e8e8;
        }
        
        .tab.active {
            background: white;
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        
        .content {
            padding: 40px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .result-box {
            margin-top: 30px;
            padding: 25px;
            border-radius: 12px;
            background: #f8f9fa;
            border-left: 5px solid #667eea;
        }
        
        .result-box.success {
            background: #d4edda;
            border-left-color: #28a745;
        }
        
        .result-box.warning {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        
        .result-box.error {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .metric {
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 15px 25px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #667eea;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .table tr:hover {
            background: #f5f5f5;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .card {
            padding: 20px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }
        
        .status-badge.success {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-badge.error {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Bio Farma Procurement Assistant</h1>
            <p>AI-powered procurement automation for pharmaceutical manufacturing</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('chat')">💬 General Chat</button>
            <button class="tab" onclick="showTab('create-po')">📝 Create PO</button>
            <button class="tab" onclick="showTab('validate')">✅ Validate Invoice</button>
            <button class="tab" onclick="showTab('price')">📊 Price Comparison</button>
        </div>
        
        <div class="content">
            <!-- Tab 1: General Chat -->
            <div id="chat" class="tab-content active">
                <h2>General Procurement Assistant</h2>
                <div class="form-group">
                    <label for="chat-query">Ask me anything about procurement:</label>
                    <textarea id="chat-query" placeholder="e.g., What are the approved suppliers for Amoxicillin?"></textarea>
                </div>
                <button class="btn" onclick="submitChat()">Submit Query</button>
                
                <div class="loading" id="chat-loading">
                    <div class="spinner"></div>
                    <p>Processing your query...</p>
                </div>
                
                <div id="chat-result"></div>
            </div>
            
            <!-- Tab 2: Create Purchase Order -->
            <div id="create-po" class="tab-content">
                <h2>Create Purchase Order</h2>
                <div class="grid">
                    <div class="form-group">
                        <label for="po-material">Material Code</label>
                        <input type="text" id="po-material" placeholder="e.g., RAW-001">
                    </div>
                    <div class="form-group">
                        <label for="po-quantity">Quantity</label>
                        <input type="number" id="po-quantity" value="5000" min="1">
                    </div>
                </div>
                <button class="btn" onclick="createPO()">Generate PO Recommendation</button>
                
                <div class="loading" id="po-loading">
                    <div class="spinner"></div>
                    <p>Analyzing suppliers...</p>
                </div>
                
                <div id="po-result"></div>
            </div>
            
            <!-- Tab 3: Validate Invoice -->
            <div id="validate" class="tab-content">
                <h2>Validate Invoice</h2>
                <div class="form-group">
                    <label for="invoice-number">Invoice Number</label>
                    <input type="text" id="invoice-number" placeholder="e.g., INV-2024-100">
                </div>
                <button class="btn" onclick="validateInvoice()">Validate Invoice</button>
                
                <div class="loading" id="validate-loading">
                    <div class="spinner"></div>
                    <p>Validating invoice...</p>
                </div>
                
                <div id="validate-result"></div>
            </div>
            
            <!-- Tab 4: Price Comparison -->
            <div id="price" class="tab-content">
                <h2>Price Comparison & Trends</h2>
                
                <div style="margin-bottom: 30px;">
                    <h3>Compare Suppliers</h3>
                    <div class="form-group">
                        <label for="price-material-compare">Material Code</label>
                        <input type="text" id="price-material-compare" placeholder="e.g., RAW-001">
                    </div>
                    <button class="btn" onclick="compareSuppliers()">Compare Prices</button>
                    
                    <div class="loading" id="compare-loading">
                        <div class="spinner"></div>
                        <p>Comparing prices...</p>
                    </div>
                    
                    <div id="compare-result"></div>
                </div>
                
                <hr style="margin: 40px 0; border: none; border-top: 2px solid #e0e0e0;">
                
                <div>
                    <h3>Price Trend Analysis</h3>
                    <div class="form-group">
                        <label for="price-material-trend">Material Code</label>
                        <input type="text" id="price-material-trend" placeholder="e.g., RAW-001">
                    </div>
                    <button class="btn" onclick="analyzeTrend()">Analyze Trend</button>
                    
                    <div class="loading" id="trend-loading">
                        <div class="spinner"></div>
                        <p>Analyzing trends...</p>
                    </div>
                    
                    <div id="trend-result"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Tab switching
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // General Chat
        async function submitChat() {
            const query = document.getElementById('chat-query').value;
            if (!query) {
                alert('Please enter a question');
                return;
            }
            
            showLoading('chat-loading');
            hideResult('chat-result');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                const data = await response.json();
                hideLoading('chat-loading');
                
                if (data.error) {
                    showResult('chat-result', `
                        <div class="result-box error">
                            <h3>❌ Error</h3>
                            <p>${data.error}</p>
                        </div>
                    `);
                } else {
                    showResult('chat-result', `
                        <div class="result-box success">
                            <h3>✅ Response</h3>
                            <p>${data.response}</p>
                        </div>
                    `);
                }
            } catch (error) {
                hideLoading('chat-loading');
                showResult('chat-result', `
                    <div class="result-box error">
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    </div>
                `);
            }
        }
        
        // Create PO
        async function createPO() {
            const materialCode = document.getElementById('po-material').value;
            const quantity = document.getElementById('po-quantity').value;
            
            if (!materialCode) {
                alert('Please enter material code');
                return;
            }
            
            showLoading('po-loading');
            hideResult('po-result');
            
            try {
                const response = await fetch('/api/create-po', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        material_code: materialCode,
                        quantity: parseInt(quantity)
                    })
                });
                
                const data = await response.json();
                hideLoading('po-loading');
                
                if (data.error) {
                    showResult('po-result', `
                        <div class="result-box error">
                            <h3>❌ ${data.error}</h3>
                        </div>
                    `);
                } else {
                    showResult('po-result', `
                        <div class="result-box success">
                            <h3>✅ PO Recommendation Generated</h3>
                            
                            <div class="card">
                                <h3>Material Details</h3>
                                <p><strong>${data.material_name}</strong> (${data.material_code})</p>
                                <p>Quantity: ${data.quantity} ${data.unit}</p>
                            </div>
                            
                            <div class="card">
                                <h3>Recommended Supplier</h3>
                                <p><strong>${data.recommended_supplier_name}</strong></p>
                                <p>Supplier ID: ${data.recommended_supplier_id}</p>
                                <p>Rating: ${data.supplier_rating}</p>
                                <p>Lead Time: ${data.lead_time_days} days</p>
                                <p style="color: #667eea; margin-top: 10px;">${data.reason}</p>
                            </div>
                            
                            <div class="grid">
                                <div class="metric">
                                    <div class="metric-label">Unit Price</div>
                                    <div class="metric-value">Rp ${data.unit_price.toLocaleString()}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Subtotal</div>
                                    <div class="metric-value">Rp ${data.subtotal.toLocaleString()}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Total (incl. 11% VAT)</div>
                                    <div class="metric-value">Rp ${data.total_amount.toLocaleString()}</div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>Approval Required</h3>
                                <p><strong>${data.required_approver}</strong> approval needed</p>
                                <p>Payment Terms: ${data.payment_terms}</p>
                            </div>
                        </div>
                    `);
                }
            } catch (error) {
                hideLoading('po-loading');
                showResult('po-result', `
                    <div class="result-box error">
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    </div>
                `);
            }
        }
        
        // Validate Invoice
        async function validateInvoice() {
            const invoiceNumber = document.getElementById('invoice-number').value;
            
            if (!invoiceNumber) {
                alert('Please enter invoice number');
                return;
            }
            
            showLoading('validate-loading');
            hideResult('validate-result');
            
            try {
                const response = await fetch('/api/validate-invoice', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({invoice_number: invoiceNumber})
                });
                
                const data = await response.json();
                hideLoading('validate-loading');
                
                if (data.error) {
                    showResult('validate-result', `
                        <div class="result-box error">
                            <h3>❌ ${data.error}</h3>
                        </div>
                    `);
                } else {
                    const statusClass = data.status === 'APPROVED' ? 'success' : 'warning';
                    const statusIcon = data.status === 'APPROVED' ? '✅' : '⚠️';
                    
                    let discrepanciesHtml = '';
                    if (data.discrepancies && data.discrepancies.length > 0) {
                        discrepanciesHtml = `
                            <div class="card">
                                <h3>Discrepancies Found</h3>
                                ${data.discrepancies.map(d => `<p style="color: #dc3545;">❌ ${d}</p>`).join('')}
                            </div>
                        `;
                    }
                    
                    showResult('validate-result', `
                        <div class="result-box ${statusClass}">
                            <h3>${statusIcon} ${data.status}</h3>
                            <p>${data.recommendation}</p>
                            
                            <div class="card">
                                <h3>Invoice Details</h3>
                                <p><strong>Supplier:</strong> ${data.invoice_details.supplier}</p>
                                <p><strong>Material:</strong> ${data.invoice_details.material}</p>
                                <p><strong>Invoice Total:</strong> ${data.invoice_details.invoice_total}</p>
                                <p><strong>PO Total:</strong> ${data.invoice_details.po_total}</p>
                                <p><strong>Due Date:</strong> ${data.invoice_details.due_date}</p>
                            </div>
                            
                            <div class="card">
                                <h3>Validation Checks</h3>
                                <p>${data.checks.supplier_match ? '✅' : '❌'} Supplier Match</p>
                                <p>${data.checks.material_match ? '✅' : '❌'} Material Match</p>
                                <p>${data.checks.quantity_match ? '✅' : '❌'} Quantity Match</p>
                                <p>${data.checks.price_match ? '✅' : '❌'} Price Match</p>
                                <p>${data.checks.total_match ? '✅' : '❌'} Total Match</p>
                            </div>
                            
                            ${discrepanciesHtml}
                        </div>
                    `);
                }
            } catch (error) {
                hideLoading('validate-loading');
                showResult('validate-result', `
                    <div class="result-box error">
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    </div>
                `);
            }
        }
        
        // Compare Suppliers
        async function compareSuppliers() {
            const materialCode = document.getElementById('price-material-compare').value;
            
            if (!materialCode) {
                alert('Please enter material code');
                return;
            }
            
            showLoading('compare-loading');
            hideResult('compare-result');
            
            try {
                const response = await fetch('/api/compare-prices', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({material_code: materialCode})
                });
                
                const data = await response.json();
                hideLoading('compare-loading');
                
                if (data.error) {
                    showResult('compare-result', `
                        <div class="result-box error">
                            <h3>❌ ${data.error}</h3>
                        </div>
                    `);
                } else {
                    let tableRows = '';
                    for (const [supplier, metrics] of Object.entries(data.supplier_comparison)) {
                        tableRows += `
                            <tr>
                                <td>${supplier}</td>
                                <td>Rp ${Math.round(metrics.avg_price).toLocaleString()}</td>
                                <td>Rp ${Math.round(metrics.min_price).toLocaleString()}</td>
                                <td>Rp ${Math.round(metrics.max_price).toLocaleString()}</td>
                                <td>${metrics.order_count}</td>
                            </tr>
                        `;
                    }
                    
                    showResult('compare-result', `
                        <div class="result-box">
                            <h3>${data.material_name} (${data.material_code})</h3>
                            <p>Unit: ${data.unit}</p>
                            
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Supplier</th>
                                        <th>Avg Price</th>
                                        <th>Min Price</th>
                                        <th>Max Price</th>
                                        <th>Orders</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${tableRows}
                                </tbody>
                            </table>
                        </div>
                    `);
                }
            } catch (error) {
                hideLoading('compare-loading');
                showResult('compare-result', `
                    <div class="result-box error">
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    </div>
                `);
            }
        }
        
        // Analyze Trend
        async function analyzeTrend() {
            const materialCode = document.getElementById('price-material-trend').value;
            
            if (!materialCode) {
                alert('Please enter material code');
                return;
            }
            
            showLoading('trend-loading');
            hideResult('trend-result');
            
            try {
                const response = await fetch('/api/price-trend', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({material_code: materialCode})
                });
                
                const data = await response.json();
                hideLoading('trend-loading');
                
                if (data.error) {
                    showResult('trend-result', `
                        <div class="result-box error">
                            <h3>❌ ${data.error}</h3>
                        </div>
                    `);
                } else {
                    showResult('trend-result', `
                        <div class="result-box">
                            <h3>${data.material_name} (${data.material_code})</h3>
                            <p>Period: ${data.period}</p>
                            
                            <div class="grid">
                                <div class="metric">
                                    <div class="metric-label">Starting Price</div>
                                    <div class="metric-value">${data.starting_price}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Current Price</div>
                                    <div class="metric-value">${data.current_price}</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Change</div>
                                    <div class="metric-value">${data.change_percent}</div>
                                </div>
                            </div>
                            
                            <div class="card">
                                <p><strong>Trend:</strong> ${data.trend}</p>
                                <p><strong>Average Volatility:</strong> ${data.avg_volatility}</p>
                            </div>
                        </div>
                    `);
                }
            } catch (error) {
                hideLoading('trend-loading');
                showResult('trend-result', `
                    <div class="result-box error">
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    </div>
                `);
            }
        }
        
        // Helper functions
        function showLoading(id) {
            document.getElementById(id).classList.add('active');
        }
        
        function hideLoading(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        function showResult(id, html) {
            document.getElementById(id).innerHTML = html;
        }
        
        function hideResult(id) {
            document.getElementById(id).innerHTML = '';
        }
    </script>
</body>
</html>
"""

# ====================== ROUTES ======================

@app.route('/')
def index():
    """Render main HTML page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """General chat endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        if not agent_loaded:
            return jsonify({'error': 'AI Agent not loaded. Please ensure embeddings are created.'}), 500
        
        response = agent.query(query)
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-po', methods=['POST'])
def api_create_po():
    """Create purchase order recommendation"""
    try:
        data = request.get_json()
        material_code = data.get('material_code', '')
        quantity = data.get('quantity', 0)
        
        if not material_code or quantity <= 0:
            return jsonify({'error': 'Invalid material code or quantity'}), 400
        
        result = po_creator.suggest_po(material_code, quantity)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-invoice', methods=['POST'])
def api_validate_invoice():
    """Validate invoice against PO"""
    try:
        data = request.get_json()
        invoice_number = data.get('invoice_number', '')
        
        if not invoice_number:
            return jsonify({'error': 'No invoice number provided'}), 400
        
        result = invoice_validator.validate(invoice_number)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-prices', methods=['POST'])
def api_compare_prices():
    """Compare prices across suppliers"""
    try:
        data = request.get_json()
        material_code = data.get('material_code', '')
        
        if not material_code:
            return jsonify({'error': 'No material code provided'}), 400
        
        result = price_comparator.compare_suppliers(material_code)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------- PRICE TREND API ----------------
@app.route('/api/price-trend', methods=['POST'])
def api_price_trend():
    """Analyze price trends"""
    try:
        data = request.get_json()
        material_code = data.get('material_code', '').strip()

        if not material_code:
            return jsonify({'error': 'No material code provided'}), 400

        result = price_comparator.price_trend(material_code)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------- HEALTH CHECK API ----------------
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent_loaded': agent_loaded,
        'timestamp': pd.Timestamp.now().isoformat()
    }), 200


# ====================== MAIN ======================
if __name__ == '__main__':
    print("=" * 60)
    print("🏭 Bio Farma Procurement Assistant - Flask Server")
    print("=" * 60)
    print(f"✅ Agent loaded: {agent_loaded}")
    print(f"🌐 Starting server on http://localhost:5000")
    print(f"📡 API Documentation:")
    print(f"   POST /api/chat             - General chat")
    print(f"   POST /api/create-po        - Create PO recommendation")
    print(f"   POST /api/validate-invoice - Validate invoice")
    print(f"   POST /api/compare-prices   - Compare supplier prices")
    print(f"   POST /api/price-trend      - Analyze price trends")
    print(f"   GET  /health               - Health check")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
