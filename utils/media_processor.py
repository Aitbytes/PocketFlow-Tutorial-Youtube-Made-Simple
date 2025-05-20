from typing import Dict, Optional
import os
import whisper

from moviepy import VideoFileClip
from openai import OpenAI

from youtube_processor import get_video_info

def process_media_input(source: str, input_type: str) -> Dict:
    """
    Process either YouTube URL or local video file to extract information.
    
    Args:
        source: YouTube URL or local file path
        input_type: Either "youtube" or "local"
        
    Returns:
        Dict containing video information:
        {
            "title": str,          # Video title or filename
            "transcript": str,     # Full transcript
            "thumbnail_url": str,  # Thumbnail URL (YouTube) or None (local)
            "video_id": str,       # YouTube video ID or None (local)
            "duration": float,     # Video duration in seconds
        }
        
    Raises:
        ValueError: If input_type is invalid or file/URL processing fails
    """
    if input_type not in ["youtube", "local"]:
        raise ValueError("input_type must be either 'youtube' or 'local'")

    if input_type == "youtube":
        info = get_video_info(source)
        if "error" in info:
            raise ValueError(f"YouTube processing error: {info['error']}")
            
        # Get video duration using VideoFileClip
        try:
            from pytube import YouTube
            yt = YouTube(source)
            duration = yt.length
        except:
            duration = None
            
        return {
            "title": info["title"],
            "transcript": info["transcript"],
            "thumbnail_url": info["thumbnail_url"],
            "video_id": info["video_id"],
            "duration": duration
        }
    
    else:  # local file
        if not os.path.exists(source):
            raise ValueError(f"Local file not found: {source}")
            
        # Get basic video info
        video = VideoFileClip(source)
        duration = video.duration
        
        # Extract audio and transcribe
        audio = video.audio
        audio_path = "temp_audio.wav"
        audio.write_audiofile(audio_path)
        
        # Check file size
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)  # Convert to MB
        
        if file_size_mb > 20:
            print("Spliting the audio")
            # Split audio into chunks
            full_transcript = []
            chunk_duration = (20 / file_size_mb) * video.duration  # Calculate chunk size that will result in ~25MB files
            
            for start_time in range(0, int(video.duration), int(chunk_duration)):
                end_time = min(start_time + chunk_duration, video.duration)
                chunk = VideoFileClip(source).subclipped(start_time, end_time)
                chunk_audio = chunk.audio
                
                chunk_path = f"temp_audio_chunk_{start_time}.wav"
                chunk_audio.write_audiofile(chunk_path)
                
                # Transcribe chunk
                client = OpenAI()
                print(f"Processing chunk {start_time}-{end_time}, size: {os.path.getsize(chunk_path) / (1024 * 1024):.2f} MB")
                with open(chunk_path, "rb") as audio_file:

                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                full_transcript.append(result.text)
                
                # Clean up chunk
                os.remove(chunk_path)
                chunk.close()
                
            transcript = " ".join(full_transcript)
            
        else:
            # Transcribe using OpenAI API
            client = OpenAI()
            with open(audio_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcript = result.text
        
        # Clean up
        os.remove(audio_path)
        video.close()
        
        return {
            "title": os.path.basename(source),
            "transcript": transcript,
            "thumbnail_url": None,
            "video_id": None,
            "duration": duration
        }

if __name__ == "__main__":
    # Test YouTube
    print("Testing the media processor")
    yt_url = "https://www.youtube.com/watch?v=_1f-o0nqpEI"
    try:
        yt_result = process_media_input(yt_url, "youtube")
        print("YouTube test successful:")
        print(f"Title: {yt_result['title']}")
        print(f"Transcript preview: {yt_result['transcript'][:150]}...")
    except Exception as e:
        print(f"YouTube test failed: {e}")
    
    # Test local file
    local_file = "test_video.mp4"
    if os.path.exists(local_file):
        try:
            local_result = process_media_input(local_file, "local")
            print("\nLocal file test successful:")
            print(f"Title: {local_result['title']}")
            print(f"Transcript preview: {local_result['transcript'][:150]}...")
        except Exception as e:
            print(f"Local file test failed: {e}")

