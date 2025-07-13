from flask import Flask, request, jsonify
import os
import time
import traceback
from openai import OpenAI
from flask_cors import CORS
import sys
from flask import Response, stream_with_context


app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Replace with your actual Vector Store ID and Assistant ID
VECTOR_STORE_ID = "vs_6824f56c052081919f25de6844131737"
ASSISTANT_ID = "asst_lY2FkYc4pSomJSDF0H8lLCFN"

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
            uploaded_file = client.vector_stores.files.upload_and_poll(
                vector_store_id=VECTOR_STORE_ID,
                file=f
            )
        file_id = uploaded_file.id
        UPLOADED_FILES.append({"file_id": file_id, "name": file.filename})
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
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Poll with timeout
        for _ in range(60):  # max 60 seconds
            run_status = client.beta.threads.runs.retrieve(
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
        messages = client.beta.threads.messages.list(thread_id=thread.id, limit=1)
        final_message = messages.data[0].content[0].text.value

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
        # Sample document data
        sample_documents = [
            {"file_id": "file_123", "name": "example.txt"},
            {"file_id": "file_456", "name": "report.pdf"},
            {"file_id": "file_789", "name": "presentation.pptx"}
        ]
        return jsonify({
            "documents": sample_documents
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch document list: {str(e)}"}), 500


@app.route("/gethistorical", methods=["GET"])
def get_historical():
    try:
        # Sample historical conversation data
        sample_historical_data = [
            {"question": "What is AI?", "answer": "AI stands for Artificial Intelligence."},
            {"question": "Explain machine learning.", "answer": "Machine learning is a subset of AI that involves training algorithms to learn patterns from data."},
            {"question": "What is OpenAI?", "answer": "OpenAI is an AI research and deployment company."}
        ]
        return jsonify({
            "history": sample_historical_data
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
