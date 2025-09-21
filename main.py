"""Main API server for Kitchen"""

import uvicorn
from orchestrator.main import app

if __name__ == "__main__":
    uvicorn.run(
        "orchestrator.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
