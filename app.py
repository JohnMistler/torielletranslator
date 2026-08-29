import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI()

# HTML page with upload UI
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Torielle Translator</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
        .upload-box { border: 2px dashed #ccc; padding: 30px; border-radius: 8px; margin-bottom: 20px; }
        #result { background: #f4f4f4; padding: 20px; border-radius: 8px; white-space: pre-wrap; text-align: left; }
    </style>
</head>
<body>
    <h1>Torielle Translator 🎓</h1>
    <p>Upload a photo of handwriting to decode it!</p>
    
    <div class="upload-box">
        <input type="file" id="imageInput" accept="image/*">
        <br><br>
        <button onclick="translateImage()">Translate Handwriting</button>
    </div>
    
    <h3>Translation Output:</h3>
    <div id="result">Translation will appear here...</div>

    <script>
        async function translateImage() {
            const input = document.getElementById('imageInput');
            const resultDiv = document.getElementById('result');
            
            if (!input.files[0]) {
                alert('Please select an image first!');
                return;
            }
            
            resultDiv.innerText = "Decoding professor's hieroglyphics...";
            
            const formData = new FormData();
            formData.append('file', input.files[0]);
            
            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                resultDiv.innerText = data.translation || data.error;
            } catch (err) {
                resultDiv.innerText = "Error decoding image.";
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
        image_bytes = await file.read()
        
        # Initialize Gemini API Client using GEMINI_API_KEY environment variable
        client = genai.Client()
        
        prompt = """
        You are the official 'Torielle Translator'. Transcribe the handwritten notes in this photo into plain English text.
        
        Known handwriting quirks for this author:
        - Lowercase 'a' looks like the Greek letter theta (θ).
        - Lowercase 's' looks like a triangle (Δ).
        - The number '9' looks like a lowercase 'g'.
        
        Return ONLY the decoded English text.
        """
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=file.content_type),
                prompt
            ]
        )
        return {"translation": response.text}
    except Exception as e:
        return {"error": str(e)}
