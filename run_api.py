"""
Run API Server
"""
import uvicorn
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add app directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

