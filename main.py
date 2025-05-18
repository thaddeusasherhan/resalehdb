from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.form["locationInput"]
    return f"Processed: {data}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
