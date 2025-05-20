# Explain Youtube Podcast To Me Like I'm 5

## Project Requirements
This project takes either a YouTube podcast URL or a local video file, extracts the transcript, identifies key topics and Q&A pairs, simplifies them for children, and generates an HTML report with the results.

## Utility Functions

1. **LLM Calls** (`utils/call_llm.py`)

2. **Media Processing** (`utils/media_processor.py`)
   - Process YouTube URLs: Get video title, transcript and thumbnail
   - Process local files: Extract audio, transcribe, get metadata
   - Common interface for both input types

3. **HTML Generator** (`utils/html_generator.py`)
   - Create formatted report with topics, Q&As and simple explanations

## Flow Design

The application flow consists of several key steps organized in a directed graph:

1. **Video Processing**: Extract transcript and metadata from YouTube URL
2. **Topic Extraction**: Identify the most interesting topics (max 5)
3. **Question Generation**: For each topic, generate interesting questions (3 per topic)
4. **Topic Processing**: Batch process each topic to:
   - Rephrase the topic title for clarity
   - Rephrase the questions
   - Generate ELI5 answers
5. **HTML Generation**: Create final HTML output

### Flow Diagram

```mermaid
flowchart TD
    videoProcess[Process YouTube URL] --> topicsQuestions[Extract Topics & Questions]
    topicsQuestions --> contentBatch[Content Processing]
    contentBatch --> htmlGen[Generate HTML]
    
    subgraph contentBatch[Content Processing]
        topicProcess[Process Topic]
    end
```

## Data Structure

The shared memory structure will be organized as follows:

```python
shared = {
    "input": {
        "type": str,          # "youtube" or "local"
        "source": str,        # YouTube URL or local file path
    },
    "video_info": {
        "title": str,          # Video title or filename
        "transcript": str,     # Full transcript
        "thumbnail_url": str,  # Thumbnail URL (YouTube) or None (local)
        "video_id": str,       # YouTube video ID or None (local)
        "duration": float,     # Video duration in seconds
    },
    "topics": [
        {
            "title": str,              # Original topic title
            "rephrased_title": str,    # Clarified topic title
            "questions": [
                {
                    "original": str,      # Original question
                    "rephrased": str,     # Clarified question
                    "answer": str         # ELI5 answer
                },
                # ... more questions
            ]
        },
        # ... more topics
    ],
    "html_output": str  # Final HTML content
}
```

## Node Designs

### 1. ProcessVideoInput
- **Purpose**: Process either YouTube URL or local video file to extract information
- **Design**: Regular Node (no batch/async)
- **Data Access**: 
  - Read: Input type and source from shared store
  - Write: Video information to shared store
- **Implementation Details**:
  - Detects input type (YouTube URL vs local file)
  - For YouTube: Uses YouTube API to get metadata and transcript
  - For local files: 
    - Extracts audio from video
    - Uses speech-to-text to generate transcript
    - Gets basic metadata (filename, duration)
  - Provides unified output format for downstream nodes

### 2. ExtractTopicsAndQuestions
- **Purpose**: Extract interesting topics from transcript and generate questions for each topic
- **Design**: Regular Node (no batch/async)
- **Data Access**:
  - Read: Transcript from shared store
  - Write: Topics with questions to shared store
- **Implementation Details**:
  - First extracts up to 5 interesting topics from the transcript
  - For each topic, immediately generates 3 relevant questions
  - Returns a combined structure with topics and their associated questions

### 3. ProcessTopic
- **Purpose**: Batch process each topic for rephrasing and answering
- **Design**: BatchNode (process each topic)
- **Data Access**:
  - Read: Topics and questions from shared store
  - Write: Rephrased content and answers to shared store

### 4. GenerateHTML
- **Purpose**: Create final HTML output
- **Design**: Regular Node (no batch/async)
- **Data Access**:
  - Read: Processed content from shared store
  - Write: HTML output to shared store

