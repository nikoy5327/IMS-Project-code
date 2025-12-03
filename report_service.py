from database.connection import SessionLocal
from database.models import Product
from fpdf import FPDF
import os
from datetime import datetime
import json

class ReportService:
    
    @staticmethod
    def inventory_report():
        """Get current inventory data as list of dictionaries"""
        session = SessionLocal()
        try:
            products = session.query(Product).all()
            
            report_data = []
            for p in products:
                item = {
                    "id": p.id,
                    "name": p.name,
                    "qty": p.current_quantity,
                    "threshold": p.reorder_threshold,
                    "unit_price": float(p.unit_price) if p.unit_price else 0.0,
                    "total_value": float(p.current_quantity * p.unit_price) if p.unit_price else 0.0
                }
                
                # Handle category safely
                if p.category:
                    item["category"] = p.category.name
                else:
                    item["category"] = "Uncategorized"
                
                report_data.append(item)
            
            return report_data
        except Exception as e:
            print(f"Error in inventory_report: {e}")
            return []
        finally:
            session.close()
    
    @staticmethod
    def generate_inventory_pdf(report_date=None):
        """Generate PDF report and save to file"""
        if report_date is None:
            report_date = datetime.now()
        
        # Get inventory data
        inventory_data = ReportService.inventory_report()
        
        # Create PDF
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "INVENTORY REPORT", ln=True, align="C")
        
        # Date
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, f"Generated: {report_date.strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(10)
        
        # Summary
        total_items = sum(item["qty"] for item in inventory_data)
        total_value = sum(item["total_value"] for item in inventory_data)
        low_stock = sum(1 for item in inventory_data if item["qty"] <= item["threshold"])
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "SUMMARY", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"Total Products: {len(inventory_data)}", ln=True)
        pdf.cell(0, 8, f"Total Items: {total_items}", ln=True)
        pdf.cell(0, 8, f"Total Value: ${total_value:,.2f}", ln=True)
        pdf.cell(0, 8, f"Low Stock Items: {low_stock}", ln=True)
        pdf.ln(10)
        
        # Table Header
        pdf.set_font("Arial", "B", 11)
        col_widths = [60, 25, 35, 25, 30, 35]
        headers = ["Product", "Qty", "Category", "Threshold", "Unit Price", "Total Value"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C")
        pdf.ln()
        
        # Table Rows
        pdf.set_font("Arial", "", 10)
        for item in inventory_data:
            # Highlight low stock
            if item["qty"] <= item["threshold"]:
                pdf.set_fill_color(255, 200, 200)  # Light red
            else:
                pdf.set_fill_color(255, 255, 255)
            
            # Product name (truncate)
            name = item["name"][:25] + "..." if len(item["name"]) > 25 else item["name"]
            pdf.cell(col_widths[0], 8, name, border=1, fill=True)
            
            # Quantity
            pdf.cell(col_widths[1], 8, str(item["qty"]), border=1, align="C", fill=True)
            
            # Category
            pdf.cell(col_widths[2], 8, item["category"][:15], border=1, align="C", fill=True)
            
            # Threshold
            pdf.cell(col_widths[3], 8, str(item["threshold"]), border=1, align="C", fill=True)
            
            # Unit Price
            pdf.cell(col_widths[4], 8, f"${item['unit_price']:.2f}", border=1, align="R", fill=True)
            
            # Total Value
            pdf.cell(col_widths[5], 8, f"${item['total_value']:.2f}", border=1, align="R", ln=True, fill=True)
        
        # Footer
        pdf.ln(15)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "End of Report - Inventory Management System", ln=True, align="C")
        
        # Save PDF
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = report_date.strftime("%Y%m%d_%H%M%S")
        filename = f"inventory_report_{timestamp}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        pdf.output(filepath)
        
        return {
            "filename": filename,
            "filepath": filepath,
            "date": report_date.strftime("%Y-%m-%d"),
            "summary": {
                "total_products": len(inventory_data),
                "total_items": total_items,
                "total_value": total_value,
                "low_stock_items": low_stock
            }
        }
    
    @staticmethod
    def list_reports():
        """List all generated PDF reports"""
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            return []
        
        files = []
        for filename in os.listdir(reports_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                
                # Parse date from filename
                date_str = "Unknown"
                if "inventory_report_" in filename:
                    try:
                        # Extract from: inventory_report_20241203_143022.pdf
                        date_part = filename.replace("inventory_report_", "").split("_")[0]
                        if len(date_part) == 8:
                            year = date_part[0:4]
                            month = date_part[4:6]
                            day = date_part[6:8]
                            date_str = f"{year}-{month}-{day}"
                    except:
                        date_str = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d")
                
                files.append({
                    "filename": filename,
                    "report_date": date_str,
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
                    "size": f"{stat.st_size / 1024:.1f} KB"
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x["created"], reverse=True)
        return files
    
    @staticmethod
    def delete_report(filename):
        """Delete a report file"""
        try:
            filepath = os.path.join("reports", filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except:
            return False
        
