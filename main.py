from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import uuid
import json
import logging

# Initialize FastAPI app
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store uploaded images
UPLOAD_DIR = "./uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Path to the storage file
STORAGE_FILE = "storage.json"

# Ensure the storage file exists
if not os.path.exists(STORAGE_FILE):
    with open(STORAGE_FILE, "w") as f:
        json.dump([], f)

# Define InventoryItem model
class InventoryItem(BaseModel):
    id: str
    name: str
    description: str
    category: str
    image_url: str

# Load inventory from storage
def load_inventory():
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading inventory: {str(e)}")

# Save inventory to storage
def save_inventory(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.get("/hello", name="getHello")
async def read_root():
    return {"message": "Hello, Evans!"}

@app.post("/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image and store it in the UPLOAD_DIR.
    Returns the URL of the uploaded image.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    # Generate a unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save the file locally
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Use the current server URL for the image URL
    file_url = f"/images/{file_id}_{file.filename}"
    return JSONResponse(content={"image_url": file_url})

@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve uploaded images.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(file_path)

@app.get("/inventory", response_model=List[InventoryItem])
async def get_inventory():
    """
    Retrieve all inventory items.
    """
    return load_inventory()

@app.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: str):
    """
    Retrieve a specific inventory item by ID.
    """
    inventory = load_inventory()
    item = next((item for item in inventory if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    return item

@app.post("/inventory", response_model=InventoryItem)
async def create_inventory_item(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image_url: str = Form(...),
):
    """
    Create a new inventory item.
    """
    inventory = load_inventory()
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": name,
        "description": description,
        "category": category,
        "image_url": image_url,
    }
    inventory.append(item)
    save_inventory(inventory)
    return item

@app.put("/inventory/{item_id}", response_model=InventoryItem)
async def update_inventory_item(
    item_id: str,
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image_url: str = Form(...),
):
    """
    Update an existing inventory item.
    """
    inventory = load_inventory()
    item = next((item for item in inventory if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    
    item.update({
        "name": name,
        "description": description,
        "category": category,
        "image_url": image_url,
    })
    save_inventory(inventory)
    return item

@app.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    """
    Delete an inventory item by ID.
    """
    inventory = load_inventory()
    item = next((item for item in inventory if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    
    inventory.remove(item)
    save_inventory(inventory)
    return {"detail": f"Item with ID {item_id} has been deleted."}

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
