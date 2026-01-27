"""
Use Case 3: Price Comparison across suppliers and time
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.config import RAW_DATA_DIR


import pandas as pd
from src.config import RAW_DATA_DIR

class PriceComparator:
    def __init__(self):
        self.materials_df = pd.read_csv(RAW_DATA_DIR / "materials.csv")
        self.suppliers_df = pd.read_csv(RAW_DATA_DIR / "suppliers.csv")
        self.pos_df = pd.read_csv(RAW_DATA_DIR / "purchase_orders.csv")
        self.price_history_df = pd.read_csv(RAW_DATA_DIR / "price_history.csv")
    
    def compare_suppliers(self, material_code: str):
        """Compare prices across all suppliers for a material"""
        # Get recent POs for this material
        material_pos = self.pos_df[self.pos_df['material_code'] == material_code]
        
        if material_pos.empty:
            return {"error": f"No purchase history for {material_code}"}
        
        # Group by supplier
        supplier_prices = material_pos.groupby('supplier_name').agg({
            'unit_price_idr': ['mean', 'min', 'max', 'count']
        }).round(0)
        
        supplier_prices.columns = ['avg_price', 'min_price', 'max_price', 'order_count']
        supplier_prices = supplier_prices.sort_values('avg_price')
        
        return {
            "material_code": material_code,
            "material_name": material_pos.iloc[0]['material_name'],
            "unit": material_pos.iloc[0]['unit'],
            "supplier_comparison": supplier_prices.to_dict('index')
        }
    
    def price_trend(self, material_code: str):
        """Show price trend over time"""
        history = self.price_history_df[
            self.price_history_df['material_code'] == material_code
        ].sort_values('year_month')
        
        if history.empty:
            return {"error": f"No price history for {material_code}"}
        
        # Calculate trend
        first_price = history.iloc[0]['avg_unit_price_idr']
        last_price = history.iloc[-1]['avg_unit_price_idr']
        change_pct = ((last_price / first_price) - 1) * 100
        
        return {
            "material_code": material_code,
            "material_name": history.iloc[0]['material_name'],
            "period": f"{history.iloc[0]['year_month']} to {history.iloc[-1]['year_month']}",
            "starting_price": f"Rp {first_price:,.0f}",
            "current_price": f"Rp {last_price:,.0f}",
            "change_percent": f"{change_pct:+.2f}%",
            "trend": "Increasing" if change_pct > 0 else "Decreasing",
            "avg_volatility": f"{history['price_volatility_percent'].mean():.1f}%",
            "monthly_data": history[['year_month', 'avg_unit_price_idr', 'supplier_id']].to_dict('records')
        }