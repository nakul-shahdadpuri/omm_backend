from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, world! Your API is live 🚀"})

if __name__ == "__main__":
    app.run()
