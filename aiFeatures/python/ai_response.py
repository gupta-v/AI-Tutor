import os
import time
import mistune  # Markdown to HTML conversion
import sys
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


load_dotenv()
# Initialize AI Tutor Models
llm_shunya = ChatGoogleGenerativeAI(model="gemini-1.5-flash")   # Shunya LLM
llm_pratham = ChatGoogleGenerativeAI(model="gemini-1.5-flash")  # Pratham LLM
llm_dviteey = ChatGoogleGenerativeAI(model="gemini-2.0-flash")  # Dviteey LLM

@dataclass
class Message:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class ChatSession:
    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    max_history_length: int = 20  # Default limit for messages to store
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        # Implement truncation if history exceeds max length
        if len(self.messages) >= self.max_history_length:
            # Remove oldest messages (keep the most recent)
            self.messages = self.messages[-(self.max_history_length-1):]
        
        self.messages.append(Message(role=role, content=content))
    
    def get_formatted_history(self) -> str:
        """Return the chat history in a formatted string for context."""
        formatted = ""
        for msg in self.messages:
            formatted += f"{msg.role.capitalize()}: {msg.content}\n\n"
        return formatted
    
    def get_langchain_messages(self) -> List[Tuple[str, str]]:
        """Return chat history in LangChain message format."""
        return [(msg.role, msg.content) for msg in self.messages]

# Session manager to handle multiple chat sessions
class ChatSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, session_id: str) -> ChatSession:
        """Create a new chat session."""
        self.sessions[session_id] = ChatSession(session_id=session_id)
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing chat session by ID."""
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> ChatSession:
        """Get an existing session or create a new one if it doesn't exist."""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Prompt templates with updated system messages and chat history context
def create_shunya_prompt_with_history(session: ChatSession):
    """Create a prompt template that includes chat history."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an experienced AI Tutor specializing in personalized education. "
                   "You will be provided with web scraped content and a user query. "
                   "Your goal is to provide clear, thoughtful explanations tailored to the student's "
                   "learning needs. Use bold for key concepts, create structured lists for step-by-step "
                   "explanations, and provide examples when appropriate. Maintain context from previous "
                   "exchanges to create a cohesive learning experience. Address knowledge gaps "
                   "compassionately and encourage critical thinking. Adjust your teaching style based on "
                   "the student's responses and questions."
                   "Incorporate relevant web information when available to provide up-to-date and accurate information."),
        *session.get_langchain_messages(),
        ("human",  "User Query: {query}\n\n"
                  "Web Scraped Content: {scraped_content}\n\n"
                  "Please provide a helpful, educational response.")
    ])

        
def create_pratham_prompt_with_history(session: ChatSession):
    """Create a pratham prompt template with chat history for retrieval-based responses."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an AI Assistant that generates educational content based on retrieved information. "
                  "Your role is to analyze the data retrieved from the knowledge database contents "
                  "create an informative, well-structured topic explanations that address the user's query. "
                  "Focus on extracting the most relevant information from the retrieved data, organizing it "
                  "logically, and presenting it in a way that builds upon previous conversation context. "
                  "Identify key concepts, create logical connections between ideas, and ensure "
                  "the information is factually accurate based on the retrieved data."
                  "When using web-scraped information, prioritize recent and authoritative content."),
        *session.get_langchain_messages(),
        ("human", "User Query: {query}\n\n"
                  "Vector Database Retrieval Response: {retrieved}\n\n"
                  "Your Task: Generate a comprehensive topic explanation based on the retrieved information "
                  "while considering the conversation history and addressing the specific query.")
    ])

def create_dviteey_prompt_with_history(session: ChatSession):
    """Create a dviteey prompt template with chat history for response verification."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Tutor responsible for delivering the highest quality educational content. "
                   "Your task is to review and enhance the educational material provided to you. "
                   "This is a confidential verification process - you must NEVER mention or acknowledge the existence "
                   "of any prior assistant, response generation process, or verification chain in your output. "
                   "\n\n"
                   "You will receive a user query, retrieved information, and a draft response. Analyze all Three "
                   "to ensure accuracy, completeness, and pedagogical effectiveness. Focus on:\n"
                   "- Correcting any factual errors based on the retrieved information\n"
                   "- Ensuring the response is relevant to the user's query\n"
                   "- Improving clarity and structure for better learning outcomes\n"
                   "- Enhancing explanations with appropriate examples or analogies\n"
                   "- Maintaining continuity with previous conversation context\n"
                   "- Ensuring the response directly addresses the user's learning needs\n"
                   "\n"
                   "Your final output should appear as a direct response to the user with no indication "
                   "that any verification or refinement process occurred. The user should perceive your "
                   "response as coming directly from their tutor, not as a refined version of another system's output."),
        *session.get_langchain_messages(),
        ("human", "User Query: {query}\n\n"
                  "Draft Educational Content: {response}\n\n"
                  "Retrieved Reference Information: {retrieved}\n\n"
                  "Your Task: Provide a refined, improved educational response directly addressing the "
                  "user's query. Ensure factual accuracy based on the retrieved information while  maintaining "
                  "the conversational flow from previous exchanges.")
    ])

# Markdown to HTML formatter
def format_response(response):
    """Converts AI response from Markdown to clean HTML."""
    if not response:
        return "No response from AI Tutor."
    return mistune.markdown(response)

# Function for standard response (without retrieval)
def generate_response_without_retrieval(session_id: str, prompt: str,scraped_content: str, session_manager: ChatSessionManager):
    """Generates AI response using a single LLM (no retrieval) with chat history."""
    try:
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Add user message to history
        session.add_message("human", prompt)
        
        # Create prompt with history and generate response
        prompt_template = create_shunya_prompt_with_history(session)
        shunya_response = (prompt_template | llm_shunya | StrOutputParser()).invoke({
            "query": prompt,
            "scraped_content": scraped_content,
            })
        
        # Add assistant response to history
        session.add_message("assistant", shunya_response)
        
        return format_response(shunya_response)
    except Exception as e:
        return f"Error: {str(e)}"

# Function for retrieval-based response (with verification)
def generate_response_with_retrieval(session_id: str, prompt: str, retrieved_data: str, session_manager: ChatSessionManager):
    """Generates AI response using two LLMs (retrieval-based verification) with chat history."""
    try:
        # Get or create session
        session = session_manager.get_or_create_session(session_id)

        # Add user message to history
        session.add_message("human", prompt)

        # Step 1: Generate initial response with history
        pratham_prompt = create_pratham_prompt_with_history(session)
        pratham_response = (pratham_prompt | llm_pratham | StrOutputParser()).invoke({
            "query": prompt,
            "retrieved": retrieved_data,
        })

        # Step 2: Verify & refine response using retrieval data and history
        dviteey_prompt = create_dviteey_prompt_with_history(session)
        dviteey_response = (dviteey_prompt | llm_dviteey | StrOutputParser()).invoke({
            "query": prompt,
            "retrieved": retrieved_data,
            "response": pratham_response,
        })
        
        # Add assistant response to history
        session.add_message("assistant", dviteey_response)
        
        return format_response(dviteey_response)
    except Exception as e:
        return f"Error: {str(e)}"
    

# Test Run
if __name__ == "__main__":
    # Create a session manager
    session_manager = ChatSessionManager()
    
    # Use a consistent session ID for the test
    test_session_id = "test_session_001"
    
    while True:
        user_input = input("Ask something (or type 'exit' to quit): ")
        
        if user_input.lower() == 'exit':    
            break
        # Simulating retrieval decision
        use_retrieval = input("Use retrieval? (yes/no): ").strip().lower() == "yes"
        
        scraped_text = input("Enter Scraped data: ") # Simulating retrieval data
        
        if use_retrieval:
            retrieved_info = input("Enter retrieved data: ")  # Simulating retrieval data
            response = generate_response_with_retrieval(
                test_session_id, user_input, scraped_text, retrieved_info, session_manager
            )
        else:
            response = generate_response_without_retrieval(
                test_session_id, user_input, scraped_text, session_manager
            )
            
        print("AI Tutor Response:", response)
        
        # Show chat history for demonstration
        session = session_manager.get_session(test_session_id)
        print("\n--- Chat History ---")
        print(session.get_formatted_history())
        print("-------------------\n")