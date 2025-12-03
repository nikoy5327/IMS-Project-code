from flask import Blueprint, jsonify
from database.connection import SessionLocal
from database.models import Alert

alert_bp = Blueprint("alerts", __name__)

@alert_bp.get("/")
def get_alerts():
    session = SessionLocal()
    alerts = session.query(Alert).all()

    data = []
    for a in alerts:
        data.append({
            "product": a.product.name if a.product else "Unknown",  # corrected
            "msg": a.message,
            "status": a.status
        })

    session.close()
    return jsonify(data)


