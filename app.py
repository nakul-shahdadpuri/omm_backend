from flask import Flask, request, jsonify
import os
import time
import traceback
from openai import OpenAI
from flask_cors import CORS
import sys
from flask import Response, stream_with_context
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi


app = Flask(__name__)
CORS(app)

# OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Replace with your actual Vector Store ID and Assistant ID
VECTOR_STORE_ID = "vs_6824f56c052081919f25de6844131737"
ASSISTANT_ID = "asst_lY2FkYc4pSomJSDF0H8lLCFN"

# MongoDB Atlas connection
uri = "mongodb+srv://nakulshahdadpuri45:AsOAnjioznHUljC7@cluster0.iaimdcl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(uri, tls=True, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
db = mongo_client["omm"]

try:
    print(db.list_collection_names())
except Exception as e:
    print("❌ Failed to connect:", e)

# Inserting into MongoDB
def insert_into_table(collection_name, document):
    """
    Inserts a document into the specified MongoDB collection.
    :param collection_name: Name of the collection
    :param document: Document to insert (dict)
    """
    try:
        collection = db[collection_name]
        collection.insert_one(document)
        print(f"✅ Document inserted into '{collection_name}' collection.")
    except Exception as e:
        print(f"❌ Failed to insert document: {e}")


def display_all_from_table(collection_name):
    """
    Displays all documents from the specified MongoDB collection.
    :param collection_name: Name of the collection
    """
    try:
        data = []
        collection = db[collection_name]
        print(f"\n📄 All Documents in '{collection_name}':")
        for doc in collection.find({}, {"_id": 0}):  # Exclude `_id` field
            data.append(doc)
        return data
    except Exception as e:
        print(f"❌ Failed to fetch documents: {e}")


UPLOADED_FILES = []

@app.route("/api/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    try:
        with open(temp_path, "rb") as f:
            uploaded_file = openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=VECTOR_STORE_ID,
                file=f
            )
        file_id = uploaded_file.id

        # Insert document into MongoDB
        insert_into_table('document', {"file_id": file_id, "name": file.filename})

        return jsonify({
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "file_id": file_id
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/api/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400

    try:
        thread = openai_client.beta.threads.create()
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Poll with timeout
        for _ in range(60):  # max 60 seconds
            run_status = openai_client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception("Run failed")
            time.sleep(1)
        else:
            raise TimeoutError("Run did not complete in time")

        # Fetch final response (only last message)
        messages = openai_client.beta.threads.messages.list(thread_id=thread.id, limit=1)
        final_message = messages.data[0].content[0].text.value

        # Insert conversation into MongoDB
        insert_into_table('conversation_history', {"question": question, "answer": final_message})

        return jsonify({
            "text": final_message,
            "sourceSnippet": "Generated using OpenAI Assistant"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Ask failed: {str(e)}"}), 500


@app.route("/api/ask_stream", methods=["POST"])
def ask_stream():
    def generate():
        for word in ["Hello", "from", "your", "API!", "🎉"]:
            yield word + "\n"
    return Response(
        stream_with_context(generate()),
        content_type="text/plain; charset=utf-8",
        headers={"X-Accel-Buffering": "no"}
    )


@app.route("/get_document_list", methods=["GET"])
def get_document_list():
    try:
        documents = display_all_from_table('document')
        return jsonify({
            "documents": documents
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch document list: {str(e)}"}), 500


@app.route("/gethistorical", methods=["GET"])
def get_historical():
    try:
        history = display_all_from_table('conversation_history')
        return jsonify({
            "history": history
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
