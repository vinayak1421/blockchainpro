# Import libraries 
import json
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import gridfs
from io import BytesIO
from Blockchain import Blockchain
from Block import Block

# Flask App
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # Change if using MongoDB Atlas
db = client["blockchain_files"]
fs = gridfs.GridFS(db)

# Blockchain object
blockchain = Blockchain()
# Peers list
peers = []


@app.route("/new_transaction", methods=["POST"])
def new_transaction():
    """
    Adds a new transaction and uploads file to MongoDB GridFS.
    """
    file_data = request.get_json()
    required_fields = ["user", "v_file", "file_data", "file_size"]

    for field in required_fields:
        if not file_data.get(field):
            return "Transaction does not have valid fields!", 404

    filename = secure_filename(file_data.get("v_file"))

    try:
        # Upload to GridFS
        file_id = fs.put(file_data.get("file_data").encode(), filename=filename)
        file_data["mongo_file_id"] = str(file_id)

        # Add transaction
        blockchain.add_pending(file_data)
        return "Success", 201

    except Exception as e:
        return f"Failed to upload to MongoDB: {e}", 500


@app.route("/submit", methods=["POST"])
def submit():
    """
    Uploads file using HTML form and stores in MongoDB GridFS.
    """
    if "file" not in request.files:
        return "No file part", 400

    up_file = request.files["file"]
    if up_file.filename == "":
        return "No selected file", 400

    if up_file:
        filename = secure_filename(up_file.filename)
        try:
            file_id = fs.put(up_file.read(), filename=filename)
            return f"File uploaded successfully with download link: /download/{filename}", 201
        except Exception as e:
            return f"Failed to upload file: {e}", 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """
    Downloads file from MongoDB GridFS using filename.
    """
    try:
        grid_out = fs.find_one({"filename": filename})
        if not grid_out:
            return "File not found", 404

        return send_file(BytesIO(grid_out.read()), download_name=filename, as_attachment=True)

    except Exception as e:
        return f"Download error: {e}", 500


@app.route("/chain", methods=["GET"])
def get_chain():
    """
    Returns the full blockchain with download links (if available).
    """
    chain = []
    for block in blockchain.chain:
        block_data = block.__dict__.copy()
        for tx in block_data["transactions"]:
            if "v_file" in tx:
                tx["download_link"] = f"/download/{secure_filename(tx['v_file'])}"
        chain.append(block_data)
    return json.dumps({"length": len(chain), "chain": chain})


@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
    """
    Mines pending transactions.
    """
    result = blockchain.mine()
    if result:
        return f"Block #{result} mined successfully."
    else:
        return "No pending transactions to mine."


@app.route("/pending_tx", methods=["GET"])
def get_pending_tx():
    """
    Shows unconfirmed/pending transactions.
    """
    return json.dumps(blockchain.pending)


@app.route("/add_block", methods=["POST"])
def validate_and_add_block():
    """
    Validates and adds a block.
    """
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["prev_hash"])
    hashl = block_data["hash"]
    added = blockchain.add_block(block, hashl)

    if not added:
        return "The Block was discarded by the node.", 400
    return "The block was added to the chain.", 201


# Run the app
if __name__ == "__main__":
    app.run(port=8800, debug=True)
