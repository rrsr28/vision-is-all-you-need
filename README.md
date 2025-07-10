# 📸 Vision by MCP

> Give your Large Language Model eyes — using MCP

This project is a **FastMCP-based camera server** that enables **real-time webcam access** for LLM agents via Claude Desktop. It allows the LLM to interact with your camera through tool use, capturing images, and querying camera info — all through natural prompts.

<hr>

## 🚀 Features

✅ Claude-compatible camera tooling via FastMCP  
✅ Real-time webcam access using OpenCV  
✅ Stream-based capture for faster frame reads  
✅ Automatic tool registration using `@mcp.tool()`  
✅ Image delivery as base64-encoded PNGs using `mcp.types.ImageContent`


## 🧰 Available Tools (MCP-Registered)

| Tool | Description |
|------|-------------|
| `list_cameras()` | List all connected webcam device IDs |
| `get_camera_info(camera_id)` | Get resolution and FPS of a camera |
| `start_camera(camera_id)` | Start streaming camera in a background thread |
| `capture_from_stream(camera_id)` | Get the latest frame from that running stream |
| `stop_camera(camera_id)` | Stop the camera stream |
| `capture_image(camera_id)` | Capture a one-time image snapshot (non-streaming) |

> All tools are automatically exposed to Claude Desktop via `MCP`, no schemas required.

---

## Example Prompts for Claude Desktop

Here’s how to use the camera tools in a natural, intuitive way inside Claude Desktop. Claude will infer and call the tools via the MCP protocol.

### 📷 Single Image Capture
```
Can you show me what the webcam sees right now?
```

### 🔁 Start Stream
```
Start watching the camera and let me know if anything changes.
```

### 🖼️ Get Live Frame (from stream)
```
Get the current frame from the active webcam stream.
```

### 🛑 Stop Stream
```
You can stop the webcam now.
```

### 🎥 Get Camera Info
```
What is the resolution and FPS of my webcam?
```

### 📋 List Cameras
```
Which cameras are connected to my machine?
````

---

## Setup

1. **Install requirements**
   
  ```bash
  pip install fastmcp opencv-python Pillow
  ````

2. **In Claude Desktop:**

   * Open Settings → Developer → Edit Config  
   * Add the MCP Server

---

## 🛠 Internals

* `FastMCP("camera-server")`: Registers the agent with MCP
* `@mcp.tool()`: Automatically exposes functions as tools to Claude
* `ImageContent`: Standard return type for images to Claude
* OpenCV is used to interact with your webcam
* Pillow is used to encode frames as PNG

---

## 📂 Project Structure

```
camera_server.py      # FastMCP camera tooling server
README.md             # You're reading it
mcp.json              # MCP Configuration
```

---

## ✨ Future Ideas

* Add face detection or object recognition
* Record video segments on request
* Detect motion from stream frames
* Save captured frames to disk
* GUI wrapper using Gradio or Tkinter

---

Made with ❤️ by rrsr28

Title inspired by “Attention is All You Need” — but this time, it’s your LLM that’s watching you 👀
