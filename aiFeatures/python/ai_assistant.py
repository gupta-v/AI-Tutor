import os
import sys
import html2text
from dotenv import load_dotenv

# Add aiFeatures/python to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "aiFeatures/python")))

from ai_response import generate_response_without_retrieval, generate_response_with_retrieval, ChatSessionManager
from web_scraping import web_response
from speech_to_text import speech_to_text
from text_to_speech import say as text_to_speech
from rag_pipeline import retrieve_answer, index_pdfs

# Load environment variables
load_dotenv()

# Create a session manager to handle chat context
session_manager = ChatSessionManager()
default_session_id = "user_session_001"  # Default session ID

# Ask user whether they want to input a single file, folder, or nothing
def initialize_rag():
    choice = input("\nDo you want to load a (1) single PDF file, (2) Multiple PDFs, (3) Folder of PDFs or (0) nothing? (Enter 0, 1, 2 or 3): ").strip()

    if choice == "1":
        pdf_path = input("\nEnter the full path to the PDF file: ").strip()
        if not os.path.exists(pdf_path) or not pdf_path.endswith(".pdf"):
            print("\n❌ Invalid file. Please enter a valid PDF file path.")
            return None
        return index_pdfs(pdf_path)  # Use the unified index_pdfs function 
    
    elif choice == "2":
        file_paths = input("\nEnter the paths of PDF files (separated by commas): ").strip()
        pdf_list = [path.strip() for path in file_paths.split(",")]  # Split and clean paths

        # Check if all files exist
        invalid_files = [pdf for pdf in pdf_list if not os.path.exists(pdf)]
        
        if invalid_files:
            print(f"\n❌ The following files do not exist: {', '.join(invalid_files)}")
            return None
    
        return index_pdfs(pdf_list)  # Pass the list of valid PDFs
    
    elif choice == "3":
        folder_path = input("\nEnter the folder path containing PDF files: ").strip()
        if not os.path.exists(folder_path):
            print("\n❌ Folder does not exist. Please enter a valid path.")
            return None
        return index_pdfs(folder_path)  # Use unified function with folder path
    
    elif choice == "0":
        print("\n⚠️ No PDFs will be loaded. The assistant will work without document-based responses.")
        return None  # No document-based indexing
    
    else:
        print("\n❌ Invalid choice. Please enter 0, 1, 2 or 3.")
        return None

# Initialize RAG based on user input
print("\nInitializing RAG system...")
vector_store = initialize_rag()

if vector_store:
    print("\n✅ RAG system initialized successfully!")
else:
    print("\n⚠️ No PDFs loaded. The AI will answer questions without document-based knowledge.")
    
# Markdown converter
def convert_to_markdown(html_text):
    converter = html2text.HTML2Text()
    converter.ignore_links = False  # Set to True if you want to remove links
    converter.body_width = 0  # Prevents automatic line wrapping
    return converter.handle(html_text)

def main():
    print("\nWelcome to AI Assistant!")
    text_to_speech("Welcome to AI Assistant!")
    mode = input("\nChoose mode (text [1] / voice [2]): ").strip().lower()

    if mode in ["1", "text"]:
        user_input = input("\nType your question: ")
    elif mode in ["2", "voice"]:
        print("\nSpeak now...")
        text_to_speech("Speak now...")
        user_input = speech_to_text()
        print("You said:", user_input)
        text_to_speech("You said: " + user_input)
    else:
        print("\nInvalid mode. Choose 'text' (1) or 'voice' (2).")
        return
    scraped_text= web_response(user_input)  # Call web_response function to get the scraped content
    # Step 1: Check if retrieval is needed
    retrieved_info = retrieve_answer(user_input, vector_store) if vector_store else ""
    
    
    if retrieved_info:
        print("\nRetrieved information:")
        print(retrieved_info)

    # Step 2: Choose AI response function based on retrieval
    if retrieved_info:
        response = generate_response_with_retrieval(default_session_id, user_input, scraped_text, retrieved_info, session_manager)
    else:
        response = generate_response_without_retrieval(default_session_id, user_input, scraped_text, session_manager)

    # Format & print AI response
    formatted_response = convert_to_markdown(response)
    print("\nAI Response:", formatted_response)

    # Step 3: Speak the response if in voice mode
    if mode in ["2", "voice"]:
        text_to_speech(response)

if __name__ == "__main__":
    main()