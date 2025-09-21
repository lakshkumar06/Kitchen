"""Main entry point for Kitchen orchestrator"""

from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    uvicorn.run("orchestrator.main:app", host="0.0.0.0", port=8000, reload=True)