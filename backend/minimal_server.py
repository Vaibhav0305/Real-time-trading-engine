from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VittCott Minimal Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "VittCott is running!", "status": "success"}

@app.get("/test")
def test():
    return {"message": "Test endpoint working!"}

if __name__ == "__main__":
    import uvicorn
    print("Starting VittCott server on localhost:8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
