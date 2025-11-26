"""
Carols Inventory Monthly Inventory Alert System
Sends monthly inventory reports and low stock alerts
"""

import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging
from pathlib import Path

class InventoryAlertSystem:
    def __init__(self, config_file="inventory_config.json"):
        self.config = self.load_config(config_file)
        self.inventory_data = self.load_inventory_data()
        self.setup_logging()
    
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            default_config = {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_shop@example.com",
                    "sender_password": "your_password",
                    "recipients": ["owner@yourshop.com", "manager@yourshop.com"]
                },
                "inventory": {
                    "low_stock_threshold": 10,
                    "critical_stock_threshold": 5,
                    "data_file": "inventory_data.json"
                },
                "alert_settings": {
                    "send_email_alerts": True,
                    "log_to_file": True,
                    "monthly_report_day": 1  # 1st of every month
                }
            }
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    def load_inventory_data(self):
        """Load current inventory data."""
        data_file = self.config["inventory"]["data_file"]
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Sample inventory data structure
            sample_data = {
                "last_updated": datetime.now().isoformat(),
                "products": {
                    "product_001": {
                        "name": "Widget A",
                        "current_stock": 25,
                        "min_stock_level": 15,
                        "category": "Electronics",
                        "supplier": "Tech Supplies Inc",
                        "last_ordered": "2024-01-15"
                    },
                    "product_002": {
                        "name": "Gadget B", 
                        "current_stock": 8,
                        "min_stock_level": 12,
                        "category": "Electronics",
                        "supplier": "Tech Supplies Inc",
                        "last_ordered": "2024-01-20"
                    },
                    "product_003": {
                        "name": "Tool C",
                        "current_stock": 3,
                        "min_stock_level": 10,
                        "category": "Hardware",
                        "supplier": "Hardware World",
                        "last_ordered": "2024-01-10"
                    }
                }
            }
            self.save_inventory_data(sample_data)
            return sample_data
    
    def save_inventory_data(self, data=None):
        """Save inventory data to file."""
        if data is None:
            data = self.inventory_data
        data_file = self.config["inventory"]["data_file"]
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('inventory_alerts.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_inventory(self):
        """Analyze inventory and identify low stock items."""
        low_stock_threshold = self.config["inventory"]["low_stock_threshold"]
        critical_threshold = self.config["inventory"]["critical_stock_threshold"]
        
        low_stock_items = []
        critical_stock_items = []
        
        for product_id, product in self.inventory_data["products"].items():
            current_stock = product["current_stock"]
            min_stock = product.get("min_stock_level", low_stock_threshold)
            
            if current_stock <= critical_threshold:
                critical_stock_items.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "category": product["category"],
                    "supplier": product["supplier"]
                })
            elif current_stock <= min_stock:
                low_stock_items.append({
                    "product_id": product_id,
                    "name": product["name"], 
                    "current_stock": current_stock,
                    "min_stock": min_stock,
                    "category": product["category"],
                    "supplier": product["supplier"]
                })
        
        return {
            "low_stock": low_stock_items,
            "critical_stock": critical_stock_items,
            "total_products": len(self.inventory_data["products"]),
            "analysis_date": datetime.now().isoformat()
        }
    
    def generate_monthly_report(self, analysis_results):
        """Generate formatted monthly inventory report."""
        report_date = datetime.now().strftime("%B %Y")
        
        report = f"""
MONTHLY INVENTORY REPORT - {report_date}
{'=' * 50}

SUMMARY:
Total Products: {analysis_results['total_products']}
Low Stock Items: {len(analysis_results['low_stock'])}
Critical Stock Items: {len(analysis_results['critical_stock'])}

CRITICAL STOCK ITEMS (IMMEDIATE ACTION NEEDED):
{'-' * 50}
"""
        
        if analysis_results['critical_stock']:
            for item in analysis_results['critical_stock']:
                report += f"• {item['name']} (ID: {item['product_id']})\n"
                report += f"  Current Stock: {item['current_stock']} | Minimum: {item['min_stock']}\n"
                report += f"  Supplier: {item['supplier']} | Category: {item['category']}\n"
        else:
            report += "No critical stock items.\n"
        
        report += f"\nLOW STOCK ITEMS (PLAN TO REORDER):\n{'-' * 50}\n"
        
        if analysis_results['low_stock']:
            for item in analysis_results['low_stock']:
                report += f"• {item['name']} (ID: {item['product_id']})\n"
                report += f"  Current Stock: {item['current_stock']} | Minimum: {item['min_stock']}\n"
                report += f"  Supplier: {item['supplier']}\n"
        else:
            report += "No low stock items.\n"
        
        report += f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
    
    def send_email_alert(self, subject, body):
        """Send email alert with inventory report."""
        if not self.config["alert_settings"]["send_email_alerts"]:
            self.logger.info("Email alerts are disabled in configuration")
            return False
        
        try:
            email_config = self.config["email"]
            msg = MimeMultipart()
            msg['From'] = email_config["sender_email"]
            msg['To'] = ", ".join(email_config["recipients"])
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["sender_email"], email_config["sender_password"])
            text = msg.as_string()
            server.sendmail(email_config["sender_email"], email_config["recipients"], text)
            server.quit()
            
            self.logger.info("Monthly inventory alert email sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def should_send_monthly_report(self):
        """Check if today is the monthly report day."""
        today = datetime.now()
        report_day = self.config["alert_settings"]["monthly_report_day"]
        return today.day == report_day
    
    def run_monthly_check(self):
        """Run the complete monthly inventory check."""
        if not self.should_send_monthly_report():
            self.logger.info("Not the monthly report day - skipping check")
            return
        
        self.logger.info("Starting monthly inventory analysis...")
        
        # Analyze inventory
        analysis_results = self.analyze_inventory()
        
        # Generate report
        report = self.generate_monthly_report(analysis_results)
        
        # Log results
        self.logger.info(f"Monthly analysis complete: {len(analysis_results['critical_stock'])} critical, {len(analysis_results['low_stock'])} low stock items")
        
        # Send email alert
        subject = f"Monthly Inventory Alert - {datetime.now().strftime('%B %Y')}"
        email_sent = self.send_email_alert(subject, report)
        
        # Save report to file
        self.save_report_to_file(report)
        
        return analysis_results
    
    def save_report_to_file(self, report):
        """Save report to a text file."""
        report_filename = f"inventory_report_{datetime.now().strftime('%Y%m')}.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        self.logger.info(f"Report saved to {report_filename}")
    
    def update_product_stock(self, product_id, new_quantity):
        """Update stock level for a product."""
        if product_id in self.inventory_data["products"]:
            self.inventory_data["products"][product_id]["current_stock"] = new_quantity
            self.inventory_data["last_updated"] = datetime.now().isoformat()
            self.save_inventory_data()
            self.logger.info(f"Updated {product_id} stock to {new_quantity}")
            return True
        return False

def main():
    """Main function to run the inventory alert system."""
    print("Small Shop Inventory Alert System")
    print("=" * 40)
    
    # Initialize the system
    inventory_system = InventoryAlertSystem()
    
    # Run monthly check
    results = inventory_system.run_monthly_check()
    
    if results:
        print(f"\nMonthly check completed:")
        print(f"- Critical items: {len(results['critical_stock'])}")
        print(f"- Low stock items: {len(results['low_stock'])}")
        print(f"- Check logs for details: inventory_alerts.log")
    else:
        print("Not scheduled for monthly report today.")

if __name__ == "__main__":
    main()
