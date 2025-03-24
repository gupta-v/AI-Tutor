import os
import mistune  # Using mistune instead of markdown2
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Initialize AI Tutor Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Define AI Tutor prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI Tutor that provides clear, structured explanations. "
                   "Use bold for important concepts, and lists for step-by-step explanations."),
        ("human", "{query}"),
    ]
)

# Create AI Tutor chain (Prompt → Gemini → Output Parser)
chain = prompt_template | llm | StrOutputParser()

def format_response(response):
    """Converts AI response from Markdown to clean HTML without extra styling issues."""
    if not response:
        return "No response from AI Tutor."
    
    # Convert Markdown to HTML using mistune
    html_response = mistune.markdown(response)

    return html_response  # Now, clean HTML without unnecessary formatting issues

def generate_response(prompt):
    """Generates AI response using LangChain Chain for AI Tutor."""
    try:
        result = chain.invoke({"query": prompt})
        return format_response(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Test Run
if __name__ == "__main__":
    user_input = input("Ask something: ")
    print("AI Tutor Response:", generate_response(user_input))
