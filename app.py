from flask import Flask, request, jsonify
import os
import time
import traceback
from openai import OpenAI
from flask_cors import CORS


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
    question = data.get("question", "")

    if not question.strip():
        return jsonify({"error": "Question cannot be empty"}), 400

    try:
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Workaround: update assistant with vector store before using
        assistant = client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            tool_resources={
                "file_search": {"vector_store_ids": [VECTOR_STORE_ID]}
            }
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        print("Starting retrieve")
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise Exception("Run failed")
            time.sleep(1)

        print("After retrieve", run_status.status)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        final_message = messages.data[0].content[0].text.value

        return jsonify({
            "text": final_message,
            "sourceSnippet": "Generated using OpenAI Assistant"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Ask failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
