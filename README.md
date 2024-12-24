# Inventory Management API

A FastAPI-based inventory management system with image upload capabilities and ngrok integration for external access.

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- ngrok account and authtoken

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

3. Install and configure ngrok:
   - Download and install ngrok from [ngrok.com](https://ngrok.com/download)
   - Sign up for a free account at [ngrok.com](https://ngrok.com)
   - Get your authtoken from the ngrok dashboard
   - Configure ngrok with your authtoken:
```bash
ngrok config add-authtoken your-authtoken
```

## Project Structure

```
.
├── README.md
├── main.py              # FastAPI application
├── openapi.yaml         # OpenAPI specification
├── plugin_manifest.json # Plugin manifest
├── static/             # Static files directory
│   └── logo.png        # Example logo file
├── uploaded_images/    # Directory for uploaded images
└── storage.json        # JSON file for inventory data
```

## Running the Application

1. Start the ngrok tunnel (in a separate terminal):
```bash
ngrok http 8080
```
This will display something like:
```
Forwarding    https://xxxx-xx-xx-xxx-xx.ngrok-free.app -> http://localhost:8080
```

2. Set the BASE_URL environment variable and start the FastAPI server (in another terminal):
```bash
export BASE_URL="https://xxxx-xx-xx-xxx-xx.ngrok-free.app"
uvicorn main:app --port 8080 --reload
```

## Testing the API

### 1. Test Hello World Endpoint
```bash
curl https://xxxx-xx-xx-xxx-xx.ngrok-free.app/hello
```
Expected response:
```json
{"message":"Hello, Evans!"}
```

### 2. Upload an Image
```bash
curl -X POST https://xxxx-xx-xx-xxx-xx.ngrok-free.app/images/upload -F "file=@static/logo.png"
```
Expected response:
```json
{
    "image_url": "/images/uuid_logo.png",
    "full_url": "https://xxxx-xx-xx-xxx-xx.ngrok-free.app/images/uuid_logo.png"
}
```

### 3. Create an Inventory Item
```bash
curl -X POST https://xxxx-xx-xx-xxx-xx.ngrok-free.app/inventory \
  -F "name=Company Logo" \
  -F "description=Official company logo image" \
  -F "category=Branding" \
  -F "image_url=/images/uuid_logo.png"
```
Expected response:
```json
{
    "id": "generated-uuid",
    "name": "Company Logo",
    "description": "Official company logo image",
    "category": "Branding",
    "image_url": "/images/uuid_logo.png"
}
```

### 4. List All Inventory Items
```bash
curl https://xxxx-xx-xx-xxx-xx.ngrok-free.app/inventory
```
Expected response:
```json
[
    {
        "id": "generated-uuid",
        "name": "Company Logo",
        "description": "Official company logo image",
        "category": "Branding",
        "image_url": "/images/uuid_logo.png"
    }
]
```

## API Documentation

When the server is running, you can access:
- Interactive API documentation: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/docs`
- OpenAPI specification: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/openapi.yaml`
- Plugin manifest: `https://xxxx-xx-xx-xxx-xx.ngrok-free.app/plugin_manifest.json`

## Additional Features

### Image Handling
- Images are stored locally in the `uploaded_images` directory
- URLs are stored as relative paths for portability
- Proper content-type detection for PNG, JPEG, and GIF files

### URL Management
- Development URL: `http://localhost:8080`
- Production/External URL: Your ngrok URL
- BASE_URL environment variable handles proper URL generation

### Data Storage
- Inventory data is stored in `storage.json`
- File-based storage for easy development and testing
- Images are stored in `uploaded_images` directory

## Troubleshooting

1. If the server won't start:
   - Check if port 8080 is already in use
   - Ensure all dependencies are installed
   - Verify the virtual environment is activated

2. If ngrok fails:
   - Verify your authtoken is correctly configured
   - Check if ngrok is already running in another terminal
   - Ensure the port matches your FastAPI server (8080)

3. If image upload fails:
   - Check if the `uploaded_images` directory exists
   - Verify file permissions
   - Ensure the file is a valid image (PNG, JPEG, or GIF)

## Security Notes

- This is a development setup and should be modified for production use
- Consider adding authentication for production
- Implement proper file upload validation
- Add rate limiting for production use
- Consider using cloud storage for images in production
