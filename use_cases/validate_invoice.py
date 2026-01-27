"""
Use Case 2: Validate Invoice against PO
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.config import RAW_DATA_DIR

import pandas as pd
from src.config import RAW_DATA_DIR

class InvoiceValidator:
    def __init__(self):
        self.invoices_df = pd.read_csv(RAW_DATA_DIR / "invoices.csv")
        self.pos_df = pd.read_csv(RAW_DATA_DIR / "purchase_orders.csv")
    
    def validate(self, invoice_number: str):
        """
        3-way matching: Invoice vs PO
        """
        # Get invoice
        invoice = self.invoices_df[self.invoices_df['invoice_number'] == invoice_number]
        
        if invoice.empty:
            return {"error": f"Invoice {invoice_number} not found"}
        
        invoice = invoice.iloc[0]
        
        # Get corresponding PO
        po = self.pos_df[self.pos_df['po_number'] == invoice['po_number']]
        
        if po.empty:
            return {"error": f"PO {invoice['po_number']} not found"}
        
        po = po.iloc[0]
        
        # Perform checks
        checks = {
            "invoice_number": invoice_number,
            "po_number": invoice['po_number'],
            "supplier_match": invoice['supplier_id'] == po['supplier_id'],
            "material_match": invoice['material_code'] == po['material_code'],
            "quantity_match": invoice['quantity_invoiced'] == po['quantity'],
            "price_match": invoice['unit_price_idr'] == po['unit_price_idr'],
            "total_match": invoice['total_invoice_idr'] == po['total_amount_idr'],
        }
        
        # Calculate discrepancies
        discrepancies = []
        
        if not checks['quantity_match']:
            diff = invoice['quantity_invoiced'] - po['quantity']
            discrepancies.append(f"Quantity mismatch: Invoice has {invoice['quantity_invoiced']} but PO was {po['quantity']} (diff: {diff})")
        
        if not checks['price_match']:
            diff_pct = ((invoice['unit_price_idr'] / po['unit_price_idr']) - 1) * 100
            discrepancies.append(f"Price mismatch: Invoice Rp {invoice['unit_price_idr']:,} vs PO Rp {po['unit_price_idr']:,} ({diff_pct:+.2f}%)")
        
        if not checks['total_match']:
            diff = invoice['total_invoice_idr'] - po['total_amount_idr']
            discrepancies.append(f"Total amount mismatch: Rp {diff:,}")
        
        # Overall status
        if all([checks['quantity_match'], checks['price_match'], checks['total_match']]):
            status = "APPROVED"
            recommendation = "Invoice matches PO. Recommend approval for payment."
        else:
            status = "REVIEW REQUIRED"
            recommendation = "Discrepancies found. Requires manual review before payment."
        
        return {
            "status": status,
            "checks": checks,
            "discrepancies": discrepancies,
            "recommendation": recommendation,
            "invoice_details": {
                "supplier": invoice['supplier_name'],
                "material": invoice['line_item_description'],
                "invoice_total": f"Rp {invoice['total_invoice_idr']:,}",
                "po_total": f"Rp {po['total_amount_idr']:,}",
                "due_date": invoice['due_date']
            }
        }