from flask import Flask, jsonify
   import traceback

   app = Flask(__name__)

   @app.errorhandler(Exception)
   def handle_exception(e):
       print(f"Unhandled Exception: {str(e)}")
       print(traceback.format_exc())
       return jsonify(error=str(e)), 500

   @app.route('/')
   def index():
       return jsonify({"message": "Hello, World!"})

   @app.route('/test')
   def test_route():
       return jsonify({"message": "Test route working"}), 200

   if __name__ == '__main__':
       app.run(debug=True)