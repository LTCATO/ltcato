from flask import Flask, jsonify, request
from supabase import create_client
import os
import sys
from dotenv import load_dotenv
from routes.routes import register_routes
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

def create_app():
    

    register_routes(app)

    @app.route('/_health')
    def health_check():
        return "App is running"

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)