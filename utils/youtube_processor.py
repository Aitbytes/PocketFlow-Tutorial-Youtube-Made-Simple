import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_info(url):
    """Get video title, transcript and thumbnail"""
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    
    try:
        # Get title using BeautifulSoup
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.text.replace(" - YouTube", "")
        
        # Get thumbnail
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, ('en', 'fr') )
        transcript = " ".join([entry["text"] for entry in transcript_list])
        
        return {
            "title": title,
            "transcript": transcript,
            "thumbnail_url": thumbnail_url,
            "video_id": video_id
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=_1f-o0nqpEI&t"
    result = get_video_info(test_url)
    print(f"Title: {result.get('title')}")
    print(f"Transcript: {result.get('transcript', '')[:150]}...") 
    print(f"Thumbnail URL: {result.get('thumbnail_url')}")
    print(f"Video ID: {result.get('video_id')}")
