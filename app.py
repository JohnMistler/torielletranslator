import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title> The Official Torielle Translator</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        .upload-box { border: 2px dashed #ccc; padding: 30px; border-radius: 8px; margin-bottom: 20px; }
        #result { background: #f4f4f4; padding: 20px; border-radius: 8px; white-space: pre-wrap; text-align: left; min-height: 50px; }
    </style>
</head>
<body>
    <h1>Torielle Translator V1</h1>
    <p>Upload a photo of Torielli's handwriting to convert it into readable English.</p>
    
    <div class="upload-box">
        <input type="file" id="imageInput" accept="image/*">
        <br><br>
        <button onclick="translateImage()">Translate Handwriting</button>
    </div>
    
    <h3>Translation Output:</h3>
    <div id="result">English translation will appear here...</div>

    <script>
        async function translateImage() {
            const input = document.getElementById('imageInput');
            const resultDiv = document.getElementById('result');
            
            if (!input.files[0]) {
                alert('Please select an image first!');
                return;
            }
            
            resultDiv.innerText = "Decoding unknown Torielle hieroglyphics...";
            
            const formData = new FormData();
            formData.append('file', input.files[0]);
            
            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.translation) {
                    resultDiv.innerText = data.translation;
                } else {
                    resultDiv.innerText = "Server Error: " + (data.error || "Unknown response");
                }
            } catch (err) {
                resultDiv.innerText = "Fetch Error: " + err.message;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return html_content

@app.post("/api/translate")
async def translate(file: UploadFile = File(...)):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"error": "GEMINI_API_KEY environment variable is not set on Render!"}

        image_bytes = await file.read()
        
        client = genai.Client(api_key=api_key)
        
        prompt = """
        You are the official 'Torielle Translator'. Transcribe the Torielle language in this photo into plain English text.
        
        Known handwriting quirks for this author:
        - Lowercase 'a' looks like the Greek letter theta (θ).
        - Lowercase 's' looks like a triangle (Δ).
        - The number '9' looks like a lowercase 'g'.
        
        Return ONLY the decoded English text.
        """
        
        # Uses gemini-2.5-flash which is the standard supported model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=file.content_type or "image/jpeg"),
                prompt
            ]
        )
        return {"translation": response.text}
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        return {"error": str(e)}
