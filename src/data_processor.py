"""
Convert CSV data to text documents for RAG system
"""
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import RAW_DATA_DIR, DOCUMENTS_DIR

class DataProcessor:
    def __init__(self):
        self.raw_dir = RAW_DATA_DIR
        self.docs_dir = DOCUMENTS_DIR
        
    def create_material_documents(self):
        """Convert materials.csv to individual text documents"""
        df = pd.read_csv(self.raw_dir / "materials.csv")
        output_dir = self.docs_dir / "materials"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for _, row in df.iterrows():
            doc_content = f"""MATERIAL INFORMATION
{'='*50}
Material Code: {row['material_code']}
Material Name: {row['material_name']}
Category: {row['category']}
Subcategory: {row['subcategory']}

PRICING & STOCK
Standard Price: Rp {row['standard_price']:,} per {row['unit_of_measure']}
Current Stock: {row['current_stock']} {row['unit_of_measure']}
Minimum Stock Level: {row['min_stock_level']} {row['unit_of_measure']}
Reorder Point: {row['reorder_point']} {row['unit_of_measure']}

SUPPLY CHAIN
Lead Time: {row['lead_time_days']} days
Number of Suppliers: {row['supplier_count']}
Last Purchase Date: {row['last_purchase_date']}

COMPLIANCE
GMP Required: {row['gmp_required']}
Storage Condition: {row['storage_condition']}
Criticality Level: {row['criticality']}
"""
            filepath = output_dir / f"{row['material_code']}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        print(f"✅ Created {len(df)} material documents")
    
    def create_supplier_documents(self):
        """Convert suppliers.csv to individual text documents"""
        df = pd.read_csv(self.raw_dir / "suppliers.csv")
        output_dir = self.docs_dir / "suppliers"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for _, row in df.iterrows():
            doc_content = f"""SUPPLIER INFORMATION
{'='*50}
Supplier ID: {row['supplier_id']}
Supplier Name: {row['supplier_name']}
Type: {row['supplier_type']}
Specialization: {row['category_specialization']}

LOCATION
Country: {row['country']}
City: {row['city']}
Tax ID: {row['tax_id']}

PERFORMANCE METRICS
Rating: {row['rating']}
On-Time Delivery: {row['on_time_delivery_percent']}%
Defect Rate: {row['defect_rate_percent']}%
Annual Spend: Rp {row['annual_spend_idr']:,}

TERMS
Payment Terms: {row['payment_terms_days']} days
Lead Time: {row['lead_time_days']} days
Currency: {row['currency']}

COMPLIANCE
Quality Certifications: {row['quality_certification']}
Last Audit Date: {row['last_audit_date']}
Contract Status: {row['contract_status']}

CONTACT
Contact Person: {row['contact_person']}
Email: {row['email']}
Phone: {row['phone']}
"""
            filepath = output_dir / f"{row['supplier_id']}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        print(f"✅ Created {len(df)} supplier documents")
    
    def create_po_documents(self):
        """Convert purchase_orders.csv to individual text documents"""
        df = pd.read_csv(self.raw_dir / "purchase_orders.csv")
        output_dir = self.docs_dir / "purchase_orders"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for _, row in df.iterrows():
            doc_content = f"""PURCHASE ORDER
{'='*50}
PO Number: {row['po_number']}
PO Date: {row['po_date']}
Reference PR: {row['pr_number']}
Status: {row['status']}

SUPPLIER
Supplier ID: {row['supplier_id']}
Supplier Name: {row['supplier_name']}

MATERIAL
Material Code: {row['material_code']}
Description: {row['material_name']}
Quantity: {row['quantity']} {row['unit']}
Unit Price: Rp {row['unit_price_idr']:,}

FINANCIAL
Subtotal: Rp {row['subtotal_idr']:,}
Tax ({row['tax_percent']}%): Rp {row['tax_amount_idr']:,}
Total Amount: Rp {row['total_amount_idr']:,}

DELIVERY
Expected Delivery: {row['delivery_date']}
Delivery Location: {row['delivery_location']}
Payment Terms: {row['payment_terms']}

APPROVAL
Created By: {row['created_by']}
Approved By: {row['approved_by']}
Approval Date: {row['approval_date']}

RECEIPT
Received Date: {row['received_date']}
Received Quantity: {row['received_quantity']}
Notes: {row['notes']}
"""
            filepath = output_dir / f"{row['po_number']}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        print(f"✅ Created {len(df)} PO documents")
    
    def create_invoice_documents(self):
        """Convert invoices.csv to individual text documents"""
        df = pd.read_csv(self.raw_dir / "invoices.csv")
        output_dir = self.docs_dir / "invoices"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for _, row in df.iterrows():
            doc_content = f"""INVOICE
{'='*50}
Invoice Number: {row['invoice_number']}
Invoice Date: {row['invoice_date']}
Reference PO: {row['po_number']}

SUPPLIER
Supplier ID: {row['supplier_id']}
Supplier Name: {row['supplier_name']}

LINE ITEM
Material Code: {row['material_code']}
Description: {row['line_item_description']}
Quantity Invoiced: {row['quantity_invoiced']} {row['unit']}
Unit Price: Rp {row['unit_price_idr']:,}
Line Total: Rp {row['line_total_idr']:,}

FINANCIAL
Subtotal: Rp {row['subtotal_idr']:,}
Tax ({row['tax_percent']}%): Rp {row['tax_amount_idr']:,}
Total Invoice Amount: Rp {row['total_invoice_idr']:,}

PAYMENT
Payment Terms: {row['payment_terms']}
Due Date: {row['due_date']}
Payment Status: {row['payment_status']}
Payment Date: {row['payment_date']}
Payment Method: {row['payment_method']}
Payment Reference: {row['payment_reference']}

VALIDATION
Discrepancy Flag: {row['discrepancy_flag']}
Discrepancy Type: {row['discrepancy_type']}
Discrepancy Notes: {row['discrepancy_notes']}
Validated By: {row['validated_by']}
Validation Date: {row['validation_date']}
"""
            filepath = output_dir / f"{row['invoice_number']}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc_content)
        
        print(f"✅ Created {len(df)} invoice documents")
    
    def process_all(self):
        """Process all CSV files to documents"""
        print("🔄 Converting CSV files to text documents...")
        self.create_material_documents()
        self.create_supplier_documents()
        self.create_po_documents()
        self.create_invoice_documents()
        print("✅ All documents created successfully!")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_all()