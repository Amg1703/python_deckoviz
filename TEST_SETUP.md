# DeckViz Testing Setup

This guide explains how to set up and test the three primary components of the DeckViz system:
1. The TV app (displays collections)
2. The mobile app (manages collections)
3. The data transfer protocol between the two

## Prerequisites

- Python 3.7+
- Pip (Python package manager)
- Network connectivity between your TV device and mobile device

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Additional dependencies for the Pygame TV app:

```bash
pip install pygame
```

## Testing Components

### 1. TV App Testing

The TV app displays image collections on a TV/display device. We now use the optimized Pygame-based implementation for better performance and stability:

```bash
cd "TV app"
python pygame_tv_app.py
```

When the app starts, it will:
- Initialize the display (showing demo images if no collections exist)
- Start a socket server to listen for connections from the mobile app
- Begin periodic checks for new collections based on the scheduled time

#### Controls:
- Press **ESC** key to exit the TV app
- The app will automatically detect and display new collections when received

#### Test Images

You can add test images to the `TV app/test_images` directory for initial testing.

### 2. Mobile App Testing

The mobile app allows you to create and manage collections, and send them to the TV. To test:

```bash
cd mobile_app_frontend
python mobile_app.py
```

Then open a web browser and navigate to:
- `http://127.0.0.1:5000` (if running on the same device)
- `http://[your-ip-address]:5000` (if accessing from another device)

Through the mobile app interface, you can:
- Create new collections by uploading images
- Configure display settings (duration, transitions)
- Send collections to the TV
- Test connectivity with the TV

### 3. Data Transfer Protocol Testing

The data transfer protocol can be tested in two ways:

#### A. Using the Mobile App Interface

1. Configure the TV IP address and port in the mobile app
2. Create a collection
3. Click "Send to TV" to transfer the collection

#### B. Using the Test Client

For direct testing without the mobile app interface:

```bash
cd mobile_app_frontend
python test_client.py --host [TV_IP_ADDRESS] --port 9876 --collection [PATH_TO_COLLECTION]
```

For example:
```bash
python test_client.py --host 192.168.1.100 --collection sample_collection.json
```

## Troubleshooting

If you encounter connection issues:

1. **Verify Network Connectivity**: Ensure the TV and mobile devices are on the same network
2. **Check Firewall Settings**: Make sure port 9876 is open on the TV device
3. **IP Address**: Verify you're using the correct IP address for the TV
4. **Test Connection**: Use the "Test Connection" feature in the mobile app

## Development Notes

- The TV app logs to `tv_connection.log` for debugging purposes
- The mobile app runs in debug mode by default
- For testing, you can use the localhost (127.0.0.1) if both the TV app and mobile app are running on the same device
