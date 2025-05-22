import argparse
import logging
import sys
import os
from flow import create_content_processor_flow

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
        description="Process a YouTube video or local video file to extract topics, questions, and generate ELI5 answers."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--url", 
        type=str, 
        help="YouTube video URL to process"
    )
    group.add_argument(
        "--file",
        type=str,
        help="Local video file path to process"
    )
    args = parser.parse_args()
    
    # Get input source from arguments or prompt user
    input_source = None
    input_type = None
    
    if args.url:
        input_source = args.url
        input_type = "youtube"
    elif args.file:
        input_source = args.file
        input_type = "local"
    else:
        while True:
            choice = input("Enter input type (1 for YouTube URL, 2 for local file): ").strip()
            if choice == "1":
                input_source = input("Enter YouTube URL to process: ").strip()
                input_type = "youtube"
                break
            elif choice == "2":
                input_source = input("Enter local video file path: ").strip()
                input_type = "local"
                break
            print("Invalid choice. Please enter 1 or 2.")
    
    logger.info(f"Starting content processor for {input_type}: {input_source}")

    # Create flow
    flow = create_content_processor_flow()
    
    # Initialize shared memory
    shared = {
        "input": {
            "type": input_type,
            "source": input_source
        }
    }
    
    # Run the flow
    flow.run(shared)
    
    # Report success and output file location
    print("\n" + "=" * 50)
    print("Processing completed successfully!")
    print(f"Output HTML file: {os.path.abspath('output.html')}")
    print("=" * 50 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
