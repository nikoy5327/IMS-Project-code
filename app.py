from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.inventory_routes import inventory_bp
from routes.sales_routes import sales_bp
from routes.alert_routes import alert_bp
from routes.report_routes import report_bp
from database.connection import Base, engine
from services.alert_service import AlertService

app = Flask(__name__)

# Enable CORS for all origins (frontend)
CORS(app, resources={r"/*": {"origins": "*"}})

# Create DB tables
Base.metadata.create_all(engine)

# Register Routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(inventory_bp, url_prefix="/inventory")
app.register_blueprint(sales_bp, url_prefix="/sales")
app.register_blueprint(alert_bp, url_prefix="/alerts")
app.register_blueprint(report_bp, url_prefix="/reports")

with app.app_context():
    AlertService.check_all_products()

if __name__ == "__main__":
    app.run(debug=True)


