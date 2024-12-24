from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/hello", name="getHello")
async def read_root():
    return {"message": "Hello, Evans!"}

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_spec():
    return FileResponse("openapi.yaml")

@app.get("/plugin_manifest.json", include_in_schema=False)
async def get_plugin_manifest():
    return FileResponse("plugin_manifest.json")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Add servers dynamically
@app.on_event("startup")
async def update_openapi_servers():
    if app.openapi_schema:
        app.openapi_schema["servers"] = [
            {"url": "https://a503-24-54-9-79.ngrok-free.app"}
        ]
