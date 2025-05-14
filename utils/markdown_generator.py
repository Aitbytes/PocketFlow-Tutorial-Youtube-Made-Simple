from typing import List, Dict, Any

def generate_markdown(source_info: Dict[str, Any], topics: List[Dict[str, Any]]) -> str:
    """Generate markdown report from processed content
    
    Args:
        source_info: Dictionary containing source metadata like title, type, location
        topics: List of topic dictionaries containing questions and answers
        
    Returns:
        Formatted markdown string
    """
    
    # Start with title and source info
    lines = [
        f"# {source_info['title']}",
        "",
        "## Source Information",
        f"- Type: {source_info['type']}",
        f"- Location: {source_info['location']}"
    ]
    
    if source_info.get("video_id"):
        lines.append(f"- Video ID: {source_info['video_id']}")
    if source_info.get("thumbnail_url"):
        lines.append(f"\n![Thumbnail]({source_info['thumbnail_url']})")
    
    # Add topics sections
    lines.extend([
        "",
        "## Key Technical Topics",
        ""
    ])
    
    # Add each topic with its questions and answers
    for topic in topics:
        lines.extend([
            f"### {topic['rephrased_title']}",
            ""
        ])
        
        for question in topic["questions"]:
            lines.extend([
                f"#### {question['rephrased']}",
                "",
                question["answer"],
                ""
            ])
    
    return "\n".join(lines)


def main():
    """Test function demonstrating markdown generation"""
    # Sample source info
    test_source = {
        "title": "Introduction to TensorFlow",
        "type": "Video Tutorial",
        "location": "https://youtube.com/watch?v=example",
        "video_id": "example123",
        "thumbnail_url": "https://img.youtube.com/vi/example123/maxresdefault.jpg"
    }
    
    # Sample topics with questions and answers
    test_topics = [
        {
            "rephrased_title": "TensorFlow Basics",
            "questions": [
                {
                    "rephrased": "What is TensorFlow?",
                    "answer": "TensorFlow is an open-source machine learning framework developed by Google. It provides comprehensive tools and libraries for building and deploying machine learning models."
                },
                {
                    "rephrased": "What are tensors?",
                    "answer": "Tensors are multi-dimensional arrays that serve as the fundamental data structure in TensorFlow. They can represent scalars, vectors, matrices, and higher-dimensional data."
                }
            ]
        },
        {
            "rephrased_title": "Model Building",
            "questions": [
                {
                    "rephrased": "How do you create a simple neural network?",
                    "answer": "You can create a neural network using the Keras API in TensorFlow by stacking layers using tf.keras.Sequential or the functional API. Define input layers, hidden layers, and output layers with appropriate activation functions."
                }
            ]
        }
    ]
    
    # Generate markdown
    markdown_output = generate_markdown(test_source, test_topics)
    
    # Print the result
    print("Generated Markdown:")
    print("-" * 40)
    print(markdown_output)
    print("-" * 40)


if __name__ == "__main__":
    main()

