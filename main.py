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

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")  # Default to localhost for development

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

@app.post("/images/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image and store it in the UPLOAD_DIR.
    Returns both the relative path and full URL of the uploaded image.
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

    # Create both relative path and full URL
    relative_path = f"/images/{file_id}_{file.filename}"
    file_url = f"{BASE_URL}{relative_path}"
    
    return JSONResponse(content={
        "image_url": relative_path,  # Store relative path
        "full_url": file_url        # Also provide full URL for convenience
    })

@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve uploaded images with proper content type.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    # Determine content type based on file extension
    content_type = "image/jpeg"  # default
    if filename.lower().endswith(".png"):
        content_type = "image/png"
    elif filename.lower().endswith(".gif"):
        content_type = "image/gif"
    
    return FileResponse(file_path, media_type=content_type)

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
    image_url: str = Form(...)
):
    """
    Create a new inventory item.
    Expects image_url to be a relative path returned from the upload endpoint.
    """
    inventory = load_inventory()
    item_id = str(uuid.uuid4())
    
    # Ensure image_url starts with /images/
    if not image_url.startswith("/images/"):
        raise HTTPException(status_code=400, detail="Invalid image URL format. Must start with /images/")

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
    image_url: str = Form(...)
):
    """
    Update an existing inventory item.
    """
    inventory = load_inventory()
    item = next((item for item in inventory if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    
    # Ensure image_url starts with /images/
    if not image_url.startswith("/images/"):
        raise HTTPException(status_code=400, detail="Invalid image URL format. Must start with /images/")
    
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

# Add servers dynamically
def update_openapi_servers():
    app.openapi_schema = None  # Clear cached schema
    schema = app.openapi()
    schema["servers"] = [{"url": BASE_URL}]
    app.openapi_schema = schema

@app.get("/openapi.yaml")
async def get_openapi_spec():
    update_openapi_servers()
    return JSONResponse(content=app.openapi())

@app.get("/plugin_manifest.json")
async def get_plugin_manifest():
    manifest = {
        "schema_version": "v1",
        "name_for_human": "Inventory Manager",
        "name_for_model": "inventory_manager",
        "description_for_human": "Manage your inventory with images and descriptions.",
        "description_for_model": "Plugin for managing inventory items with CRUD operations and image upload capabilities.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{BASE_URL}/openapi.yaml",
            "has_user_authentication": False
        },
        "logo_url": f"{BASE_URL}/static/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": "https://example.com/legal"
    }
    return JSONResponse(content=manifest)

app.mount("/static", StaticFiles(directory="static"), name="static")
update_openapi_servers()  # Update servers on startup
