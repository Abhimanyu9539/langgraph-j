import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tavily import TavilypiClient
from langchain_community.utilities import GoogleSerperAPIWrapper
from core.config import Config

class LLMClient:
    "LLM Client for interacting with LLM"

    def __init__(self):
        self.llm = ChatOpenAI(
            model = Config.LLM_MODEL, 
            temperature = Config.LLM_TEMPERATURE, 
            max_tokens = Config.LLM_MAX_TOKENS, 
            openai_api_key = Config.OPENAI_API_KEY
        )

        # Initialize Search Clients
        self.tavily_client = None
        self.serper_wrapper = None

        if Config.TAVILY_API_KEY:
            self.tavily_client = TavilypiClient(api_key=Config.TAVILY_API_KEY)

        if Config.SERPER_API_KEY:
            self.serper_wrapper = GoogleSerperAPIWrapper(serper_api_key=Config.SERPER_API_KEY)

    def chat_with_file(self, prompt: str, file_path: str) -> str:
        """
        Send prompt with file to OpenAI using Vision API for images or base64 for other files
        
        Args:
            prompt: Text prompt
            file_path: Path to file to analyze
            
        Returns:
            LLM response
        """
        try:
            # Validate file first
            from utils.simple_utils import validate_file
            is_valid, error_msg = validate_file(file_path)
            if not is_valid:
                return f"File validation error: {error_msg}"
            
            # Read file as base64
            import base64
            with open(file_path, 'rb') as file:
                file_content = file.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Get file extension to determine approach
            file_ext = os.path.splitext(file_path.lower())[1]
            
            if file_ext == '.pdf':
                # For PDF files, use base64 with data URL format
                content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/pdf;base64,{file_base64}"
                        }
                    }
                ]
            else:
                # For other files (DOCX, TXT), convert to text first and include in prompt
                # Since OpenAI doesn't directly support DOCX, we need to extract text
                if file_ext == '.txt':
                    # For text files, just read the content directly
                    file_text = file_content.decode('utf-8', errors='ignore')
                    full_prompt = f"{prompt}\n\nFILE CONTENT:\n{file_text}"
                    content = full_prompt
                else:
                    # For unsupported formats, return error
                    return f"File type {file_ext} is not directly supported by OpenAI API"
            
            # Create message
            if isinstance(content, list):
                message = HumanMessage(content=content)
            else:
                message = HumanMessage(content=content)
            
            response = self.llm.invoke([message])
            return response.content
            
        except Exception as e:
            return f"Error with LLM: {str(e)}"
    

    def chat(self, prompt:str) -> str:
        """
        Send text prompt to LLM using LangChain
        
        Args:
            prompt: Text prompt
            
        Returns:
            LLM response    
        """
        try: 
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.contents
        except Exception as e:
            return f"Error with LLM: {str(e)}"
    
    def search_jobs(self, query: str, max_results: int = 10) -> str:
        """
        Search for jobs using available search API
        
        Args:
            query: Job search query
            max_results: Maximum number of results
            
        Returns:
            Formatted search results
        """
        if self.tavily_client:
            return self._search_with_tavily(query, max_results)
        elif self.serper_wrapper:
            return self._search_with_serper(query)
        else:
            return "No search API available"


    def _search_with_tavily(self, query: str, max_results: int) -> str:
        """Search using Tavily API with proper client"""
        try:
            # Use Tavily's search method
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                include_domains=["indeed.com", "linkedin.com", "glassdoor.com", "hirist.com", "naukari.com"]
            )
            
            results = response.get("results", [])
            if not results:
                return "No job results found"
            
            # Format results nicely
            formatted_results = []
            for result in results:
                title = result.get("title", "")
                url = result.get("url", "")
                content = result.get("content", "")
                
                formatted_results.append(f"""
                **{title}**
                URL: {url}
                Description: {content[:300]}...
                ---""")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Tavily search error: {str(e)}"
        
    def _search_with_serper(self, query: str) -> str:
        """Search using Serper API with proper wrapper"""
        try:
            # Use GoogleSerperAPIWrapper's run method
            results = self.serper_wrapper.run(query)
            
            if not results:
                return "No job results found"
            
            return results
            
        except Exception as e:
            return f"Serper search error: {str(e)}"


# Global LLM client instance
llm_client = LLMClient()