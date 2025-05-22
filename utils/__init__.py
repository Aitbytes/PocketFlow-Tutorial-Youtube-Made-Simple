"""
Utils package for PocketFlow Tutorial Youtube Made Simple.

This package contains utility functions and helpers for video processing,
transcription, and other common operations used throughout the project.
"""
from .youtube_processor import get_video_info
from .media_processor import process_media_input
from .call_llm import call_llm

__version__ = "0.1.0"
__author__ = "a8taleb"
__license__ = "MIT"

# Import commonly used functions/classes here to make them available at package level
# Example: from .video_utils import process_video

