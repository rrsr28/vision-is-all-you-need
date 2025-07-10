import threading
import logging
import io
import cv2
from PIL import Image as PILImage
from typing import List, Dict, Any

from fastmcp import FastMCP
from fastmcp.utilities.types import Image as MCPImage
from mcp.types import ImageContent

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("camera-server")

# Track camera threads and their states
camera_streams: Dict[str, Dict[str, Any]] = {}

def _camera_stream_worker(camera_id: str) -> None:
    """Thread that continuously captures frames from a webcam."""
    cap = cv2.VideoCapture(int(camera_id))
    if not cap.isOpened():
        logger.error(f"Unable to open camera {camera_id}")
        return

    logger.info(f"Camera {camera_id}: stream started.")
    try:
        while not camera_streams[camera_id]["stop_event"].is_set():
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Camera {camera_id}: frame capture failed.")
                break
            camera_streams[camera_id]["frame"] = frame
            cv2.waitKey(1)  # Yield time to reduce CPU
    finally:
        cap.release()
        logger.info(f"Camera {camera_id}: stream stopped.")

@mcp.tool()
def list_cameras() -> List[str]:
    """Return a list of available camera device indices."""
    available = []
    for index in range(5):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available.append(str(index))
            cap.release()
    logger.info(f"Discovered cameras: {available}")
    return available

@mcp.tool()
def get_camera_info(camera_id: str) -> Dict[str, Any]:
    """Return camera resolution and FPS for the specified device."""
    cap = cv2.VideoCapture(int(camera_id))
    if not cap.isOpened():
        error_msg = f"Camera {camera_id} could not be opened."
        logger.error(error_msg)
        return {"error": error_msg}

    info = {
        "id": camera_id,
        "width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
        "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
        "fps": cap.get(cv2.CAP_PROP_FPS),
    }
    cap.release()
    logger.info(f"Camera {camera_id} info: {info}")
    return info

@mcp.tool()
def start_camera(camera_id: str) -> str:
    """
    Start a background camera thread for the specified camera.
    If already running, increments the client count.
    """
    if camera_id not in camera_streams:
        stop_event = threading.Event()
        camera_streams[camera_id] = {
            "clients": 1,
            "frame": None,
            "stop_event": stop_event,
        }
        thread = threading.Thread(
            target=_camera_stream_worker,
            args=(camera_id,),
            daemon=True
        )
        camera_streams[camera_id]["thread"] = thread
        thread.start()
        logger.info(f"Camera {camera_id} started (clients=1).")
        return f"Camera {camera_id} started."
    else:
        camera_streams[camera_id]["clients"] += 1
        count = camera_streams[camera_id]["clients"]
        logger.info(f"Camera {camera_id} already running. Clients: {count}")
        return f"Camera {camera_id} already running. Clients: {count}"

@mcp.tool()
def stop_camera(camera_id: str) -> str:
    """
    Stop a background camera stream if no clients are using it.
    """
    if camera_id not in camera_streams:
        error_msg = f"Camera {camera_id} is not active."
        logger.warning(error_msg)
        return error_msg

    camera_streams[camera_id]["clients"] -= 1
    remaining = camera_streams[camera_id]["clients"]

    if remaining <= 0:
        camera_streams[camera_id]["stop_event"].set()
        camera_streams[camera_id]["thread"].join()
        del camera_streams[camera_id]
        logger.info(f"Camera {camera_id} stopped.")
        return f"Camera {camera_id} stopped."
    else:
        logger.info(f"Camera {camera_id} still active. Clients: {remaining}")
        return f"Camera {camera_id} still running. Clients: {remaining}"

@mcp.tool()
def capture_image(camera_id: str) -> ImageContent:
    """
    Capture a single frame from the camera and return it as an image.
    """
    cap = cv2.VideoCapture(int(camera_id))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {camera_id}.")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError(f"Failed to capture image from camera {camera_id}.")

    image = _convert_frame_to_image(frame)
    logger.info(f"Captured image from camera {camera_id}")
    return image.to_image_content()

@mcp.tool()
def capture_from_stream(camera_id: str) -> ImageContent:
    """
    Return the latest frame from an active camera stream.
    """
    if camera_id not in camera_streams:
        raise ValueError(f"Camera {camera_id} is not streaming.")

    frame = camera_streams[camera_id]["frame"]
    if frame is None:
        raise RuntimeError(f"No frame available yet for camera {camera_id}.")

    image = _convert_frame_to_image(frame)
    logger.info(f"Retrieved stream frame from camera {camera_id}")
    return image.to_image_content()

# Utility to encode OpenCV frame to FastMCP Image
def _convert_frame_to_image(frame) -> MCPImage:
    """Convert a NumPy image frame to a FastMCP Image object (PNG format)."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = PILImage.fromarray(rgb_frame)
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return MCPImage(data=buffer.getvalue(), format="png")


if __name__ == "__main__":
    try:
        logger.info("Starting FastMCP camera server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user.")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
