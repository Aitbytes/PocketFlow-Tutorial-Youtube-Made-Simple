from typing import List, Dict, Any, Tuple
import yaml
import logging
from pocketflow import Node, BatchNode, Flow
from utils.call_llm import call_llm
from utils.media_processor import MediaProcessor
from utils.markdown_generator import generate_markdown

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the specific nodes for the YouTube Content Processor

class ProcessMediaSource(Node):
    """Process input source (YouTube URL or local file)"""
    def prep(self, shared):
        """Get source from shared"""
        return shared.get("source", "")
    
    def exec(self, source):
        """Process media source"""
        if not source:
            raise ValueError("No source provided")
        
        logger.info(f"Processing source: {source}")
        processor = MediaProcessor()
        source_info = processor.process_source(source)
        
        return source_info
    
    def post(self, shared, prep_res, exec_res):
        """Store source information in shared"""
        shared["source_info"] = exec_res
        logger.info(f"Title: {exec_res.get('title')}")
        logger.info(f"Source type: {exec_res.get('type')}")
        logger.info(f"Transcript length: {len(exec_res.get('transcript', ''))}")
        return "default"

class ExtractTopicsAndQuestions(Node):
    """Extract interesting topics and generate questions from the video transcript"""
    def prep(self, shared):
        """Get transcript and title from video_info"""
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        title = video_info.get("title", "")
        return {"transcript": transcript, "title": title}
    
    def exec(self, data):
        """Extract topics and generate questions using LLM"""
        transcript = data["transcript"]
        title = data["title"]
        
        # Single prompt to extract topics and questions together
        prompt = f"""
You are an expert content analyzer. Given a YouTube video transcript, identify at most 5 most interesting topics discussed and generate at most 3 most thought-provoking questions for each topic.
These questions don't need to be directly asked in the video. It's good to have clarification questions.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript}

Format your response in YAML:

```yaml
topics:
  - title: |
        First Topic Title
    questions:
      - |
        Question 1 about first topic?
      - |
        Question 2 ...
  - title: |
        Second Topic Title
    questions:
        ...
```
        """
        
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        

        parsed = yaml.safe_load(yaml_content)
        raw_topics = parsed.get("topics", [])
        
        # Ensure we have at most 5 topics
        raw_topics = raw_topics[:5]
        
        # Format the topics and questions for our data structure
        result_topics = []
        for topic in raw_topics:
            topic_title = topic.get("title", "")
            raw_questions = topic.get("questions", [])
            
            # Create a complete topic with questions
            result_topics.append({
                "title": topic_title,
                "questions": [
                    {
                        "original": q,
                        "rephrased": "",
                        "answer": ""
                    }
                    for q in raw_questions
                ]
            })
        
        return result_topics
    
    def post(self, shared, prep_res, exec_res):
        """Store topics with questions in shared"""
        shared["topics"] = exec_res
        
        # Count total questions
        total_questions = sum(len(topic.get("questions", [])) for topic in exec_res)
        
        logger.info(f"Extracted {len(exec_res)} topics with {total_questions} questions")
        return "default"

class ProcessContent(BatchNode):
    """Process each topic for rephrasing and answering"""
    def prep(self, shared):
        """Return list of topics for batch processing"""
        topics = shared.get("topics", [])
        video_info = shared.get("video_info", {})
        transcript = video_info.get("transcript", "")
        
        batch_items = []
        for topic in topics:
            batch_items.append({
                "topic": topic,
                "transcript": transcript
            })
        
        return batch_items
    
    def exec(self, item):
        """Process a topic using LLM"""
        topic = item["topic"]
        transcript = item["transcript"]
        
        topic_title = topic["title"]
        questions = [q["original"] for q in topic["questions"]]
        
        prompt = f"""You are a content simplifier for children. Given a topic and questions from a YouTube video, rephrase the topic title and questions to be clearer, and provide simple ELI5 (Explain Like I'm 5) answers.

TOPIC: {topic_title}

QUESTIONS:
{chr(10).join([f"- {q}" for q in questions])}

TRANSCRIPT EXCERPT:
{transcript}

For topic title and questions:
1. Keep them catchy and interesting, but short

For your answers:
1. Format them using HTML with <b> and <i> tags for highlighting. 
2. Prefer lists with <ol> and <li> tags. Ideally, <li> followed by <b> for the key points.
3. Quote important keywords but explain them in easy-to-understand language (e.g., "<b>Quantum computing</b> is like having a super-fast magical calculator")
4. Keep answers interesting but short

Format your response in YAML:

```yaml
rephrased_title: |
    Interesting topic title in 10 words
questions:
  - original: |
        {questions[0] if len(questions) > 0 else ''}
    rephrased: |
        Interesting question in 15 words
    answer: |
        Simple answer that a 5-year-old could understand in 100 words
  - original: |
        {questions[1] if len(questions) > 1 else ''}
    ...
```
        """
        
        response = call_llm(prompt)
        
        # Extract YAML content
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        
        parsed = yaml.safe_load(yaml_content)
        rephrased_title = parsed.get("rephrased_title", topic_title)
        processed_questions = parsed.get("questions", [])
        
        result = {
            "title": topic_title,
            "rephrased_title": rephrased_title,
            "questions": processed_questions
        }
        
        return result

    
    def post(self, shared, prep_res, exec_res_list):
        """Update topics with processed content in shared"""
        topics = shared.get("topics", [])
        
        # Map of original topic title to processed content
        title_to_processed = {
            result["title"]: result
            for result in exec_res_list
        }
        
        # Update the topics with processed content
        for topic in topics:
            topic_title = topic["title"]
            if topic_title in title_to_processed:
                processed = title_to_processed[topic_title]
                
                # Update topic with rephrased title
                topic["rephrased_title"] = processed["rephrased_title"]
                
                # Map of original question to processed question
                orig_to_processed = {
                    q["original"]: q
                    for q in processed["questions"]
                }
                
                # Update each question
                for q in topic["questions"]:
                    original = q["original"]
                    if original in orig_to_processed:
                        processed_q = orig_to_processed[original]
                        q["rephrased"] = processed_q.get("rephrased", original)
                        q["answer"] = processed_q.get("answer", "")
        
        # Update shared with modified topics
        shared["topics"] = topics
        
        logger.info(f"Processed content for {len(exec_res_list)} topics")
        return "default"

class GenerateMarkdown(Node):
    """Generate Markdown output from processed content"""
    def prep(self, shared):
        """Get source info and topics from shared"""
        source_info = shared.get("source_info", {})
        topics = shared.get("topics", [])
        
        return {
            "source_info": source_info,
            "topics": topics
        }
    
    def exec(self, data):
        """Generate Markdown using markdown_generator"""
        source_info = data["source_info"]
        topics = data["topics"]
        
        # Generate Markdown
        markdown_content = generate_markdown(source_info, topics)
        return markdown_content
    
    def post(self, shared, prep_res, exec_res):
        """Store Markdown output in shared"""
        shared["markdown_output"] = exec_res
        
        # Write Markdown to file
        with open("output.md", "w") as f:
            f.write(exec_res)
        
        logger.info("Generated Markdown output and saved to output.md")
        return "default"

# Create the flow
def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    # Create nodes
    process_url = ProcessMediaSource(max_retries=2, wait=10)
    extract_topics_and_questions = ExtractTopicsAndQuestions(max_retries=2, wait=10)
    process_content = ProcessContent(max_retries=2, wait=10)
    generate_html = GenerateMarkdown(max_retries=2, wait=10)
    
    # Connect nodes
    process_url >> extract_topics_and_questions >> process_content >> generate_html
    
    # Create flow
    flow = Flow(start=process_url)
    
    return flow
