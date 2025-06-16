# 標準函式庫
import os

# 第三方套件
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, session
from flask_login import UserMixin, login_user

auth_bp = Blueprint("auth", __name__)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


web_path = f"{os.getcwd()}/web"

load_dotenv(override=True)


USER_DATA = {
    "superuser": os.getenv("SUPERUSER"),
    "root": os.getenv("ROOT"),
    "admin": os.getenv("ADMIN"),
    "user": os.getenv("USER"),
    "kiosk": os.getenv("KIOSK"),
}


user_login_info = {"username": "", "password": ""}

active_superuser = []
max_login = 3


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_login_info["username"] = username
        user_login_info["password"] = password
    else:
        username = request.args.get("username")
        password = request.args.get("password")
        user_login_info["username"] = username
        user_login_info["password"] = password

    if not username or not password:
        return jsonify(success=False)

    if USER_DATA.get(username) and USER_DATA.get(username) == password:
        user = User(username)
        login_user(user)
        session["username"] = username
        return jsonify(success=True)
    else:
        return jsonify(success=False)
