# Brainstorming Backend API

This backend provides speech-to-text and text-to-speech functionality for the Kitchen brainstorming application using Google Cloud services.

## Features

- **Text-to-Speech**: Convert text to natural-sounding speech using Google Cloud Text-to-Speech
- **Speech-to-Text**: Convert audio to text using Google Cloud Speech-to-Text
- **Voice Interaction**: Handle yes/no questions and description requests
- **AI Integration**: Generate ideas using Google's Gemini AI

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. **Install Google Cloud SDK**: Follow the [official installation guide](https://cloud.google.com/sdk/docs/install)

2. **Authenticate**: 
   ```bash
   gcloud auth application-default login
   ```

3. **Enable APIs**:
   ```bash
   gcloud services enable speech.googleapis.com
   gcloud services enable texttospeech.googleapis.com
   ```

4. **Set up credentials**: Ensure your Google Cloud project has the necessary APIs enabled and you have the appropriate permissions.

### 3. Environment Variables

Create a `.env` file in the `Brainstorming` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it to your `.env` file

### 4. Run the Backend

```bash
python start_backend.py
```

The API will be available at `http://localhost:5121`

## API Endpoints

### POST /api/speak
Convert text to speech
```json
{
  "text": "Hello, how are you?"
}
```

### POST /api/transcribe
Convert audio to text
- Send audio file as multipart/form-data with key 'audio'

### POST /api/ask-yes-no
Ask a yes/no question and get voice response
```json
{
  "question": "Do you have an idea?"
}
```

### POST /api/ask-description
Ask for a description and get voice response
```json
{
  "question": "Please describe your idea",
  "max_seconds": 20
}
```

### POST /api/generate-ideas
Generate ideas using AI
```json
{
  "niche": "healthcare",
  "subNiche": "clinical",
  "area": "Patient Records",
  "industry": "Healthcare",
  "category": "Clinical"
}
```

## Frontend Integration

The frontend automatically connects to the backend when voice features are enabled. The voice flow works as follows:

1. User clicks "🎤 Start Voice Chat"
2. System asks: "Do you already have a website idea?"
3. If yes: System asks for description and records user's response
4. If no: System guides through niche selection with voice
5. All interactions are both visual and auditory

## Troubleshooting

### Common Issues

1. **"No module named 'google.cloud'"**
   - Install Google Cloud libraries: `pip install google-cloud-speech google-cloud-texttospeech`

2. **Authentication errors**
   - Run: `gcloud auth application-default login`
   - Ensure your project has the required APIs enabled

3. **Audio not playing**
   - Check browser permissions for audio
   - Ensure microphone access is granted

4. **CORS errors**
   - The backend includes CORS headers for frontend communication
   - Ensure the frontend is running on the expected port

### Testing

You can test the API endpoints using curl:

```bash
# Test text-to-speech
curl -X POST http://localhost:5121/api/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# Test yes/no question
curl -X POST http://localhost:5121/api/ask-yes-no \
  -H "Content-Type: application/json" \
  -d '{"question": "Do you have an idea?"}'
```

## Development

The backend is built with Flask and includes:
- Error handling and logging
- CORS support for frontend integration
- Audio processing utilities
- AI integration with Gemini

For development, the server runs in debug mode with auto-reload enabled.
