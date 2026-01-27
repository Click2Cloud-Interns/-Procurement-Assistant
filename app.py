import streamlit as st

st.set_page_config(
    page_title="Bio Farma Procurement Assistant",
    page_icon="🏭",
    layout="wide"
)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ProcurementAgent
from use_cases.create_po import POCreator
from use_cases.validate_invoice import InvoiceValidator
from use_cases.price_comparison import PriceComparator


# Initialize
@st.cache_resource
def load_agent():
    try:
        return ProcurementAgent()
    except Exception as e:
        st.error(f"Failed to load agent: {str(e)}")
        st.info("Please ensure you have:")
        st.code("1. Run: python src/data_processor.py")
        st.code("2. Run: python src/embeddings.py")
        st.code("3. Created .env file with Azure OpenAI credentials")
        return None

agent = load_agent()
po_creator = POCreator()
invoice_validator = InvoiceValidator()
price_comparator = PriceComparator()

# Header
st.title("🏭 Bio Farma Procurement Assistant")
st.markdown("AI-powered procurement automation for pharmaceutical manufacturing")

# Sidebar
st.sidebar.title("Use Cases")
use_case = st.sidebar.radio(
    "Select a use case:",
    ["💬 General Chat", "📝 Create Purchase Order", "✅ Validate Invoice", "📊 Price Comparison"]
)

# Use Case 1: General Chat
if use_case == "💬 General Chat":
    st.header("General Procurement Assistant")
    
    if agent is None:
        st.error("Agent not loaded. Please check setup instructions above.")
    else:
        user_query = st.text_area("Ask me anything about procurement:", height=100)
        
        if st.button("Submit"):
            if user_query:
                with st.spinner("Thinking..."):
                    try:
                        response = agent.query(user_query)
                        st.success("Response:")
                        st.write(response)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Use Case 2: Create PO
elif use_case == "📝 Create Purchase Order":
    st.header("Create Purchase Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        material_code = st.text_input("Material Code (e.g., RAW-001)")
    
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=5000)
    
    if st.button("Generate PO Recommendation"):
        if material_code:
            result = po_creator.suggest_po(material_code, quantity)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ PO Recommendation Generated")
                
                # Display in formatted way
                st.subheader("Material Details")
                st.write(f"**{result['material_name']}** ({result['material_code']})")
                st.write(f"Quantity: {result['quantity']} {result['unit']}")
                
                st.subheader("Recommended Supplier")
                st.write(f"**{result['recommended_supplier_name']}**")
                st.write(f"Supplier ID: {result['recommended_supplier_id']}")
                st.write(f"Rating: {result['supplier_rating']}")
                st.write(f"Lead Time: {result['lead_time_days']} days")
                st.info(result['reason'])
                
                st.subheader("Pricing")
                col1, col2, col3 = st.columns(3)
                col1.metric("Unit Price", f"Rp {result['unit_price']:,}")
                col2.metric("Subtotal", f"Rp {result['subtotal']:,}")
                col3.metric("Total (incl. 11% VAT)", f"Rp {result['total_amount']:,}")
                
                st.subheader("Approval Required")
                st.write(f"**{result['required_approver']}** approval needed")
                st.write(f"Payment Terms: {result['payment_terms']}")

# Use Case 3: Validate Invoice
elif use_case == "✅ Validate Invoice":
    st.header("Validate Invoice")
    
    invoice_number = st.text_input("Invoice Number (e.g., INV-2024-100)")
    
    if st.button("Validate"):
        if invoice_number:
            result = invoice_validator.validate(invoice_number)
            
            if "error" in result:
                st.error(result["error"])
            else:
                # Status
                if result['status'] == "APPROVED":
                    st.success(f"✅ {result['status']}")
                else:
                    st.warning(f"⚠️ {result['status']}")
                
                st.write(result['recommendation'])
                
                # Invoice details
                st.subheader("Invoice Details")
                details = result['invoice_details']
                col1, col2 = st.columns(2)
                col1.write(f"**Supplier:** {details['supplier']}")
                col1.write(f"**Material:** {details['material']}")
                col2.write(f"**Invoice Total:** {details['invoice_total']}")
                col2.write(f"**PO Total:** {details['po_total']}")
                col2.write(f"**Due Date:** {details['due_date']}")
                
                # Validation checks
                st.subheader("Validation Checks")
                checks = result['checks']
                col1, col2, col3 = st.columns(3)
                col1.write(f"{'✅' if checks['supplier_match'] else '❌'} Supplier Match")
                col1.write(f"{'✅' if checks['material_match'] else '❌'} Material Match")
                col2.write(f"{'✅' if checks['quantity_match'] else '❌'} Quantity Match")
                col2.write(f"{'✅' if checks['price_match'] else '❌'} Price Match")
                col3.write(f"{'✅' if checks['total_match'] else '❌'} Total Match")
                
                # Discrepancies
                if result['discrepancies']:
                    st.subheader("Discrepancies Found")
                    for disc in result['discrepancies']:
                        st.error(disc)

# Use Case 4: Price Comparison
elif use_case == "📊 Price Comparison":
    st.header("Price Comparison & Trends")
    
    tab1, tab2 = st.tabs(["Compare Suppliers", "Price Trend"])
    
    with tab1:
        st.subheader("Compare Prices Across Suppliers")
        material_code = st.text_input("Material Code (e.g., RAW-001)", key="compare")
        
        if st.button("Compare"):
            if material_code:
                result = price_comparator.compare_suppliers(material_code)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.write(f"**{result['material_name']}** ({result['material_code']})")
                    st.write(f"Unit: {result['unit']}")
                    
                    # Show comparison table
                    import pandas as pd
                    df = pd.DataFrame(result['supplier_comparison']).T
                    df['avg_price'] = df['avg_price'].apply(lambda x: f"Rp {x:,.0f}")
                    df['min_price'] = df['min_price'].apply(lambda x: f"Rp {x:,.0f}")
                    df['max_price'] = df['max_price'].apply(lambda x: f"Rp {x:,.0f}")
                    
                    st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("Price Trend Analysis")
        material_code = st.text_input("Material Code (e.g., RAW-001)", key="trend")
        
        if st.button("Analyze Trend"):
            if material_code:
                result = price_comparator.price_trend(material_code)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.write(f"**{result['material_name']}** ({result['material_code']})")
                    st.write(f"Period: {result['period']}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Starting Price", result['starting_price'])
                    col2.metric("Current Price", result['current_price'])
                    col3.metric("Change", result['change_percent'])
                    
                    st.write(f"Trend: **{result['trend']}**")
                    st.write(f"Average Volatility: {result['avg_volatility']}")
                    
                    # Show monthly data
                    import pandas as pd
                    df = pd.DataFrame(result['monthly_data'])
                    df['avg_unit_price_idr'] = df['avg_unit_price_idr'].apply(lambda x: f"Rp {x:,.0f}")
                    st.dataframe(df, use_container_width=True)