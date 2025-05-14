
from typing import Dict, Any
import os
import subprocess
import json
import requests
from utils.youtube_processor import get_video_info

class MediaProcessor:
    def __init__(self):
        self.whisper_api_key = os.getenv("WHISPER_API_KEY")
        if not self.whisper_api_key:
            raise ValueError("WHISPER_API_KEY environment variable not set")

    def process_youtube(self, url: str) -> Dict[str, Any]:
        """Process YouTube URL to get video info and transcript"""
        video_info = get_video_info(url)
        if "error" in video_info:
            raise ValueError(f"Error processing YouTube video: {video_info['error']}")
        
        return {
            "type": "youtube",
            "location": url,
            "title": video_info["title"],
            "transcript": video_info["transcript"],
            "thumbnail_url": video_info["thumbnail_url"],
            "video_id": video_info["video_id"],
            "duration": 0  # TODO: Add duration extraction
        }

    def process_local_file(self, file_path: str) -> Dict[str, Any]:
        """Process local video file to get transcript"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        # Extract audio using ffmpeg
        audio_path = "temp_audio.wav"
        cmd = [
            "ffmpeg", "-y", "-i", file_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract audio: {e}")

        # Generate transcript using Whisper API
        try:
            with open(audio_path, "rb") as audio:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.whisper_api_key}"},
                    files={"file": audio},
                    data={"model": "whisper-1"}
                )
                response.raise_for_status()
                transcript_data = response.json()
        finally:
            # Clean up temp audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

        return {
            "type": "local",
            "location": file_path,
            "title": os.path.basename(file_path),
            "transcript": transcript_data["text"],
            "thumbnail_url": None,
            "video_id": None,
            "duration": 0  # TODO: Add duration extraction
        }

    def process_source(self, source: str) -> Dict[str, Any]:
        """Process either YouTube URL or local file"""
        if source.startswith(("http://", "https://")):
            return self.process_youtube(source)
        else:
            return self.process_local_file(source)


def main():
    """Test function for MediaProcessor"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Process video files or YouTube URLs for transcription')
    parser.add_argument('source', help='YouTube URL or path to local video file')
    parser.add_argument('--pretty', action='store_true', help='Pretty print the JSON output')
    args = parser.parse_args()

    try:
        processor = MediaProcessor()
        result = processor.process_source(args.source)
        
        if args.pretty:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result))
            
    except ValueError as e:
        print(f"Configuration error: {e}")
    except FileNotFoundError as e:
        print(f"File error: {e}")
    except RuntimeError as e:
        print(f"Processing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
