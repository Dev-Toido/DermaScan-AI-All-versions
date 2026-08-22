import uvicorn
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DermaScan V5 API")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP")
    parser.add_argument("--port", type=int, default=8000, help="Port")
    parser.add_argument("--workers", type=int, default=4, help="Number of Uvicorn workers")
    
    args = parser.parse_args()
    
    # We use 'main:app' as a string so Uvicorn can spawn multiple workers
    uvicorn.run("main:app", host=args.host, port=args.port, workers=args.workers)
