from flask import jsonify
import traceback
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "error": e.name,
            "message": e.description
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # DIAGNOSTIC: Print the exact traceback to your terminal console
        print("\n--- CAUGHT UNHANDLED EXCEPTION ---")
        traceback.print_exc()
        print("----------------------------------\n")
        
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e) # Exposing message temporarily for debugging
        }), 500