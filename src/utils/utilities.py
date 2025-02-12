import os
from typing import Tuple, Optional, Dict, Any


def validate_file(file_path: str, max_size_mb: int = 5) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)"
    
    # Check file extension
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file_path.lower())[1]
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
    
    return True, None


def get_file_info(file_path: str) -> dict:
    """Get basic file information"""
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    return {
        "filename": os.path.basename(file_path),
        "extension": file_ext,
        "size_mb": round(file_size_mb, 2),
        "exists": True
    }


def format_job_search_query(job_title: str, location: str = "Remote") -> str:
    """Format job search query for search APIs"""
    job_title = job_title.strip()
    
    if location and location.lower() != "remote":
        query = f"{job_title} jobs in {location}"
    else:
        query = f"{job_title} remote jobs"
    
    return query


def format_context_for_llm(context: Dict[str, Any]) -> str:
    """Format context information for LLM prompts"""
    context_parts = []
    
    if context.get('target_job_title'):
        context_parts.append(f"Target Job: {context['target_job_title']}")
    
    if context.get('target_industry'):
        context_parts.append(f"Target Industry: {context['target_industry']}")
    
    if context.get('experience_level'):
        context_parts.append(f"Experience Level: {context['experience_level']}")
    
    if context.get('target_location'):
        context_parts.append(f"Target Location: {context['target_location']}")
    
    return " | ".join(context_parts) if context_parts else ""
