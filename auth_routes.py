from flask import Blueprint, request
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
def login():
    data = request.json
    return AuthService.login(data["username"], data["password"])
