"""Video provider adapters / helpers.

Video generation is complex; typical approaches:
- Call an external API (Pika Labs, Runway, Synthesia, etc.)
- Generate a sequence of images and use ffmpeg to combine into a video

This file contains helper stubs and a simple local ffmpeg-based renderer that expects a list of frames.
"""
from typing import List
import io
import tempfile
import os



def frames_to_mp4_bytes(frames: List[bytes], fps: int = 24) -> bytes:
    """Combine a series of image bytes into an MP4 using ffmpeg-python if available.

    This is a convenience helper; the scaffold does not ship ffmpeg binaries.
    """
    try:
        import ffmpeg
        from PIL import Image
    except Exception as e:
        raise RuntimeError("frames_to_mp4_bytes requires ffmpeg-python and Pillow: %s" % e)

    # Create a temporary directory to store frames and output
    with tempfile.TemporaryDirectory() as td:
        frame_pattern = os.path.join(td, "frame_%05d.png")
        # Write frames to files
        for idx, b in enumerate(frames, start=1):
            path = os.path.join(td, f"frame_{idx:05d}.png")
            with open(path, "wb") as fh:
                fh.write(b)

        out_path = os.path.join(td, "out.mp4")
        # Use ffmpeg to read PNG sequence and write MP4
        try:
            (ffmpeg
             .input(os.path.join(td, "frame_%05d.png"), framerate=fps)
             .output(out_path, vcodec="libx264", pix_fmt="yuv420p")
             .overwrite_output()
             .run(capture_stdout=True, capture_stderr=True))
        except ffmpeg.Error as e:
            raise RuntimeError("ffmpeg processing failed: %s" % e.stderr.decode() if hasattr(e, 'stderr') else str(e))

        # Read output bytes and return
        with open(out_path, "rb") as f:
            return f.read()
