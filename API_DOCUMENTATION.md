# DeckViz API Documentation

This document provides detailed information about the APIs and protocols used in the DeckViz system, including the communication between the mobile app and TV application.

## Overview

DeckViz consists of two main components that communicate with each other:

1. **Mobile App (Flask-based web application)**
   - Creates and manages image collections
   - Sends collections to the TV app

2. **TV App (Pygame-based display application)**
   - Receives collections from the mobile app
   - Displays images in a slideshow format

## Network Communication Protocol

### Socket Communication

The TV app and mobile app communicate using a simple socket-based protocol.

#### TV App Socket Server

The TV app runs a socket server on port 9880 by default. This server listens for incoming connections from the mobile app.

```python
# Network manager initialization in the TV app
self.network_manager = NetworkManager(collections_dir=collections_dir, port=9880)
```

#### Mobile App Socket Client

The mobile app connects to the TV app's socket server when sending collections:

```python
# Mobile app connection to the TV
def send_collection_to_tv(host, port, collection_data):
    """Send a collection to the TV app using the socket protocol"""
    try:
        # Create a socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            
            # Convert collection data to JSON string
            collection_json = json.dumps(collection_data)
            
            # Send the data with a header containing the message length
            message = f"{len(collection_json)}:{collection_json}"
            s.sendall(message.encode())
            
            # Wait for acknowledgment
            response = s.recv(1024).decode()
            
            return response == "OK"
    except Exception as e:
        # Handle connection errors
        return False
```

### Data Format

Collections are transferred as JSON objects with the following structure:

```json
{
  "title": "Collection Title",
  "description": "Collection Description",
  "date_of_creation": "YYYY-MM-DD HH:MM:SS",
  "labels": ["label1", "label2"],
  "images_id": ["path/to/image1", "path/to/image2"],
  "display_settings": {
    "duration": 5,
    "transition_effects": ["fade_in", "slide_in", "zoom_in", "flip", "crossfade"],
    "music": null
  }
}
```

#### Field Descriptions

| Field                     | Type         | Description                                                 |
|---------------------------|--------------|-------------------------------------------------------------|
| title                     | string       | Title of the collection                                     |
| description               | string       | Description of the collection                              |
| date_of_creation          | string       | Date and time when the collection was created              |
| labels                    | array        | Tags or categories for the collection                      |
| images_id                 | array        | Paths to the images in the collection                      |
| display_settings.duration | number       | Number of seconds to display each image                    |
| display_settings.transition_effects | array | Visual transitions to use between images                |
| display_settings.music    | string/null  | Path to background music file (if any)                     |

## Mobile App API Endpoints

The mobile app provides the following HTTP endpoints:

| Endpoint                  | Method | Description                                       |
|---------------------------|--------|---------------------------------------------------|
| /                         | GET    | Main page - shows list of collections             |
| /create_collection        | POST   | Create a new collection from uploaded images      |
| /edit_collection/{filename} | GET  | Edit an existing collection                       |
| /delete_collection/{filename} | GET | Delete an existing collection                    |
| /uploads/{filename}       | GET    | Serve uploaded images                            |
| /send_to_tv/{filename}    | GET    | Send a collection to the TV app                   |
| /set_tv_config            | POST   | Save TV connection settings and test connection   |
| /test_connection          | GET    | Test connection to the TV app                    |

### Example: Creating a Collection

To create a new collection, send a POST request to `/create_collection` with the following form data:

- `title`: Collection title
- `description`: Collection description
- `images`: Multiple image files
- `duration`: Display duration in seconds
- `transition`: Transition effect name

## TV App API

The TV app provides the following programmatic interfaces:

### Image Display API

The `PygameImageDisplay` class provides methods for displaying images:

```python
# Create display with image data
display = PygameImageDisplay(image_data)

# Start the display
display.start()

# Update with new images
display.update_images(new_image_data)

# Stop the display
display.stop()
```

### Network API

The `NetworkManager` class handles network communication:

```python
# Initialize network manager
network_manager = NetworkManager(collections_dir="collections", port=9880)

# Set callback for collection reception
network_manager.set_collection_received_callback(callback_function)

# Start the socket server
network_manager.start_socket_server()

# Stop the socket server
network_manager.stop_socket_server()
```

## File Storage

### Collections

Collections are stored as JSON files in the respective collections directories:

- Mobile app: `mobile_app_frontend/collections/`
- TV app: `TV app/collections/`

### Images

Images are stored in the uploads directory:

- Mobile app: `mobile_app_frontend/uploads/`
- The TV app searches for images in multiple locations, including the mobile app's uploads directory

## Error Handling

Both applications implement error handling for various scenarios:

- Network connection errors
- Missing images
- Invalid collection data
- Display initialization errors

Error details are logged to the console for debugging purposes.

## Development Notes

1. **Port Configuration**
   - The TV app listens on port 9880 by default
   - This can be modified in the TV app initialization

2. **Testing the Connection**
   - Use the mobile app's "Test Connection" feature to verify connectivity
   - Check logs for connection issues if problems occur

3. **Adding Custom Transition Effects**
   - New transition effects can be added to the TV app by extending the display code
   - Ensure the mobile app is updated to offer any new transitions
