import sys,os
from fastapi import FastAPI, Depends
from database import SessionLocal, engine
from controllers import services
import uvicorn

# load project path
# sys.path.append(os.getcwd())

API_VERSION = '/api/v1'

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "API is at /api/v1"}

app.include_router(services.app, prefix=API_VERSION)

# if __name__ == '__main__':
#   uvicorn.run(app, host="0.0.0.0", port=8080)