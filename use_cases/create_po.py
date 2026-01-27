"""
Use Case 1: Create Purchase Order
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.config import RAW_DATA_DIR, MANAGER_APPROVAL_LIMIT, VAT_RATE


import pandas as pd
from src.config import RAW_DATA_DIR, MANAGER_APPROVAL_LIMIT, VAT_RATE

class POCreator:
    def __init__(self):
        self.materials_df = pd.read_csv(RAW_DATA_DIR / "materials.csv")
        self.suppliers_df = pd.read_csv(RAW_DATA_DIR / "suppliers.csv")
    
    def suggest_po(self, material_code: str, quantity: int):
        """
        Suggest best supplier and create draft PO
        """
        # Get material info
        material = self.materials_df[self.materials_df['material_code'] == material_code]
        
        if material.empty:
            return {"error": f"Material {material_code} not found"}
        
        material = material.iloc[0]
        
        # Find suitable suppliers
        suitable_suppliers = self.suppliers_df[
            self.suppliers_df['category_specialization'].str.contains(material['category'])
        ]
        
        if suitable_suppliers.empty:
            return {"error": "No suitable suppliers found"}
        
        # Rank by rating and on-time delivery
        suitable_suppliers['score'] = (
            suitable_suppliers['on_time_delivery_percent'] * 0.6 +
            (100 - suitable_suppliers['defect_rate_percent']) * 0.4
        )
        best_supplier = suitable_suppliers.sort_values('score', ascending=False).iloc[0]
        
        # Calculate pricing
        unit_price = material['standard_price']
        subtotal = quantity * unit_price
        tax = int(subtotal * VAT_RATE)
        total = subtotal + tax
        
        # Determine approval level
        if total > MANAGER_APPROVAL_LIMIT:
            approver = "Director"
        else:
            approver = "Manager"
        
        return {
            "material_code": material_code,
            "material_name": material['material_name'],
            "quantity": quantity,
            "unit": material['unit_of_measure'],
            "recommended_supplier_id": best_supplier['supplier_id'],
            "recommended_supplier_name": best_supplier['supplier_name'],
            "supplier_rating": best_supplier['rating'],
            "lead_time_days": int(best_supplier['lead_time_days']),
            "unit_price": unit_price,
            "subtotal": subtotal,
            "tax": tax,
            "total_amount": total,
            "required_approver": approver,
            "payment_terms": f"Net {int(best_supplier['payment_terms_days'])}",
            "reason": f"Best supplier based on {best_supplier['score']:.1f}% performance score"
        }