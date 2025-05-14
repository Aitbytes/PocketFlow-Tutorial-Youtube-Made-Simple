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
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
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
    test_urls = [
        "https://www.youtube.com/watch?v=_1f-o0nqpEI&t",  # Valid URL
        "https://youtu.be/_1f-o0nqpEI",                   # Short URL
        "https://invalid-url.com/watch?v=123"             # Invalid URL
    ]
    
    print("Testing YouTube processor with multiple URLs...")
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: {url}")
        try:
            result = get_video_info(url)
            if "error" in result:
                print(f"✗ Error: {result['error']}")
                continue
                
            print("✓ Success")
            print(f"Title: {result['title']}")
            print(f"Video ID: {result['video_id']}")
            print(f"Transcript preview: {result['transcript'][:100]}...")
            print(f"Thumbnail URL: {result['thumbnail_url']}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
