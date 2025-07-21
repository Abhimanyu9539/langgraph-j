"""
Resume Analysis Multi-Agent System - Workflow State Definitions

This module defines the state structure for the LangGraph workflow that manages
the flow of data between the four main agents:
- Resume Intelligence Agent
- Job Market Research Agent  
- ATS Scoring Agent
- Career Advisory Agent
"""

from typing import List, Dict, Optional, Any, TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


# Data Models for structured information
class ResumeData(BaseModel):
    """Structured resume information extracted by Resume Intelligence Agent"""
    raw_text: str = Field(description="Raw extracted text from resume file")
    parsed_sections: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured sections: contact, summary, experience, education, skills, etc."
    )
    skills: List[str] = Field(default_factory=list, description="Extracted skills list")
    experience_years: int = Field(default=0, description="Total years of experience")
    education_level: str = Field(default="", description="Highest education level")
    job_titles: List[str] = Field(default_factory=list, description="Previous job titles")
    industries: List[str] = Field(default_factory=list, description="Industries worked in")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")


class JobMatch(BaseModel):
    """Individual job match found by Job Market Research Agent"""
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    location: str = Field(description="Job location")
    description: str = Field(description="Job description text")
    required_skills: List[str] = Field(default_factory=list, description="Required skills for the job")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    salary_range: Optional[str] = Field(default=None, description="Salary range if available")
    experience_required: Optional[str] = Field(default=None, description="Experience requirements")
    match_score: float = Field(default=0.0, description="Match score 0-1 based on resume fit")
    source: str = Field(description="Source platform: linkedin, indeed, glassdoor, etc.")
    job_url: Optional[str] = Field(default=None, description="Link to job posting")
    posted_date: Optional[str] = Field(default=None, description="When job was posted")


class ATSScore(BaseModel):
    """ATS compatibility score for a specific job"""
    job_title: str = Field(description="Job title this score is for")
    overall_score: int = Field(description="Overall ATS score 0-100")
    keyword_score: int = Field(description="Keyword matching score 0-100")
    format_score: int = Field(description="Resume format compatibility score 0-100") 
    structure_score: int = Field(description="Resume structure score 0-100")
    recommendations: List[str] = Field(
        default_factory=list,
        description="Specific recommendations to improve ATS score"
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Important keywords missing from resume"
    )
    keyword_density: Dict[str, float] = Field(
        default_factory=dict,
        description="Density of important keywords in resume"
    )


class ResumeEnhancement(BaseModel):
    """Specific points and improvements to add to resume based on job descriptions"""
    missing_skills_to_add: List[str] = Field(
        default_factory=list,
        description="Skills to add to resume skills section"
    )
    experience_bullets_to_add: List[str] = Field(
        default_factory=list,
        description="Specific bullet points to add to experience section"
    )
    keywords_to_incorporate: List[str] = Field(
        default_factory=list,
        description="Important keywords to naturally incorporate into resume"
    )
    technical_tools_to_mention: List[str] = Field(
        default_factory=list,
        description="Technical tools/software to highlight or add"
    )
    certifications_to_pursue: List[str] = Field(
        default_factory=list,
        description="Relevant certifications that would strengthen resume"
    )
    action_verbs_suggestions: List[str] = Field(
        default_factory=list,
        description="Strong action verbs to replace weak ones"
    )
    quantifiable_achievements: List[str] = Field(
        default_factory=list,
        description="Suggestions for adding metrics and numbers to achievements"
    )
    section_improvements: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Specific improvements for each resume section (summary, experience, etc.)"
    )


# Main Workflow State
class ResumeAnalysisState(TypedDict):
    """
    Main state object that flows through all nodes in the LangGraph workflow.
    Uses add_messages reducer for conversation capability while maintaining
    structured data for resume analysis.
    """
    
    # Messages with automatic reducer for conversation/logging capability
    messages: Annotated[List[BaseMessage], add_messages]
    
    # === INPUT DATA ===
    uploaded_file_path: Optional[str]  # Path to uploaded resume file
    target_job_title: Optional[str]    # Job title user is targeting
    target_industry: Optional[str]     # Industry user is targeting
    target_location: Optional[str]     # Geographic preference for jobs
    experience_level: Optional[str]    # junior, mid, senior, executive
    
    # === RESUME INTELLIGENCE AGENT OUTPUTS ===
    resume_data: Optional[ResumeData]  # Structured resume information
    parsing_errors: List[str]          # Any errors during resume parsing
    file_format: Optional[str]         # PDF, DOCX, TXT
    parsing_confidence: Optional[float] # Confidence in parsing accuracy 0-1
    
    # === JOB MARKET RESEARCH AGENT OUTPUTS ===
    matching_jobs: List[JobMatch]      # List of matching job opportunities
    job_search_errors: List[str]       # Errors during job searching
    search_query_used: Optional[str]   # Final search query used
    total_jobs_found: int              # Total number of jobs found before filtering
    
    # === ATS SCORING AGENT OUTPUTS ===
    ats_scores: List[ATSScore]         # ATS scores for each matched job
    average_ats_score: Optional[float] # Average ATS score across all jobs
    best_ats_match: Optional[str]      # Job title with highest ATS score
    
    # === CAREER ADVISORY AGENT OUTPUTS ===
    improvement_recommendations: List[str]  # General resume improvement tips
    resume_enhancements: Optional[ResumeEnhancement]  # Specific points to add to resume
    personalized_tips: List[str]       # Personalized recommendations based on job matches
    priority_improvements: List[str]   # Most important improvements to make first
    
    # === WORKFLOW CONTROL ===
    current_step: str                  # Current workflow step for tracking
    errors: List[str]                  # Global errors during workflow
    warnings: List[str]                # Non-critical warnings
    is_complete: bool                  # Whether workflow has completed successfully
    processing_time_seconds: Optional[float]  # Total processing time
    
    # === METADATA ===
    workflow_version: Optional[str]    # Version of workflow used
    timestamp_started: Optional[str]   # When analysis started
    timestamp_completed: Optional[str] # When analysis completed
    user_id: Optional[str]             # User identifier if applicable


# Helper functions for state initialization
def create_initial_state(
    uploaded_file_path: str,
    target_job_title: Optional[str] = None,
    target_industry: Optional[str] = None,
    target_location: Optional[str] = None,
    experience_level: Optional[str] = None
) -> ResumeAnalysisState:
    """
    Create an initial state object for the workflow
    
    Args:
        uploaded_file_path: Path to the uploaded resume file
        target_job_title: Optional target job title
        target_industry: Optional target industry
        target_location: Optional target location
        experience_level: Optional experience level
    
    Returns:
        Initial ResumeAnalysisState object
    """
    from datetime import datetime
    
    return ResumeAnalysisState(
        messages=[],
        uploaded_file_path=uploaded_file_path,
        target_job_title=target_job_title,
        target_industry=target_industry,
        target_location=target_location,
        experience_level=experience_level,
        resume_data=None,
        parsing_errors=[],
        file_format=None,
        parsing_confidence=None,
        matching_jobs=[],
        job_search_errors=[],
        search_query_used=None,
        total_jobs_found=0,
        ats_scores=[],
        average_ats_score=None,
        best_ats_match=None,
        improvement_recommendations=[],
        resume_enhancements=None,
        personalized_tips=[],
        priority_improvements=[],
        current_step="initialized",
        errors=[],
        warnings=[],
        is_complete=False,
        processing_time_seconds=None,
        workflow_version="1.0.0",
        timestamp_started=datetime.now().isoformat(),
        timestamp_completed=None,
        user_id=None
    )


# State validation helpers
def validate_state_transition(from_step: str, to_step: str) -> bool:
    """
    Validate that a state transition is allowed
    
    Args:
        from_step: Current step
        to_step: Next step
    
    Returns:
        True if transition is valid
    """
    valid_transitions = {
        "initialized": ["parsing_resume"],
        "parsing_resume": ["resume_parsed", "error"],
        "resume_parsed": ["searching_jobs"],
        "searching_jobs": ["jobs_found", "error"], 
        "jobs_found": ["scoring_ats"],
        "scoring_ats": ["ats_scored", "error"],
        "ats_scored": ["generating_advice"],
        "generating_advice": ["completed", "error"],
        "error": ["retry", "completed"],
        "completed": []
    }
    
    return to_step in valid_transitions.get(from_step, [])


def get_state_progress_percentage(current_step: str) -> float:
    """
    Get the progress percentage based on current step
    
    Args:
        current_step: Current workflow step
    
    Returns:
        Progress percentage 0-100
    """
    step_progress = {
        "initialized": 0.0,
        "parsing_resume": 10.0,
        "resume_parsed": 25.0,
        "searching_jobs": 40.0,
        "jobs_found": 60.0,
        "scoring_ats": 75.0,
        "ats_scored": 85.0,
        "generating_advice": 95.0,
        "completed": 100.0,
        "error": 0.0
    }
    
    return step_progress.get(current_step, 0.0)