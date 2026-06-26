from youtube_transcript_api import YouTubeTranscriptApi
import re

def fetch_youtube_transcript(url: str) -> dict:
    """Extract transcript from a YouTube URL."""
    
    # extract video id from various youtube url formats
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]
    
    video_id = None
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        return {"text": "", "error": "Could not extract video ID from URL"}
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript_list])
        duration_seconds = transcript_list[-1]["start"] if transcript_list else 0
        minutes = int(duration_seconds // 60)
        
        return {
            "text": full_text,
            "video_id": video_id,
            "duration": f"~{minutes} mins"
        }
    except Exception as e:
        return {"text": "", "error": f"Could not fetch transcript: {str(e)}"}

def detect_youtube_url(text: str) -> str | None:
    """Scan any text for a YouTube URL and return it if found."""
    pattern = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+)"
    match = re.search(pattern, text)
    return match.group(1) if match else None