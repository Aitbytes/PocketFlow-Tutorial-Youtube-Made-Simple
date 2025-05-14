import argparse
import logging
import sys
import os
from flow import create_youtube_processor_flow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("youtube_processor.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the YouTube content processor."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process a YouTube video to extract topics, questions, and generate ELI5 answers."
    )
    parser.add_argument(
        "--source", 
        type=str, 
        help="YouTube video URL or local video file path to process",
        required=False
    )
    args = parser.parse_args()
    
    # Get source from arguments or prompt user
    source = args.source
    if not source:
        source = input("Enter YouTube URL or local video file path to process: ")
    
    logger.info(f"Starting content processor for source: {source}")

    # Create flow
    flow = create_youtube_processor_flow()
    
    # Initialize shared memory
    shared = {
        "source": source
    }
    
    # Run the flow
    flow.run(shared)
    
    # Report success and output file location
    print("\n" + "=" * 50)
    print("Processing completed successfully!")
    print(f"Output Markdown file: {os.path.abspath('output.md')}")
    print("=" * 50 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
