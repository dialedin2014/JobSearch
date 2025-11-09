"""
Ally deduction orchestration service.

Coordinates resume parsing, LLM analysis, and database persistence.
"""

from typing import Dict, Any, List
import logging
from sqlalchemy.orm import Session
from src.services.resume_parser import resume_parser
from src.services.llm_service import llm_service
from src.models.resume import ParsedResume
from src.models.dream_job import DreamJobDescription
from src.models.ally_type import DeducedAllyType

logger = logging.getLogger(__name__)


class AllyDeductionService:
    """
    Service for orchestrating ally type deduction workflow.
    
    Coordinates:
    1. Resume parsing
    2. LLM-based ally type deduction
    3. Result validation and persistence
    """

    async def analyze_resume_and_dream_job(
        self,
        db: Session,
        resume_id: str,
        dream_job_id: str,
    ) -> Dict[str, Any]:
        """
        Analyze resume and dream job to deduce ally types.
        
        Args:
            db: Database session
            resume_id: ID of parsed resume
            dream_job_id: ID of dream job description
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting ally deduction for resume={resume_id}, dream_job={dream_job_id}")

        # Fetch resume and dream job
        resume = db.query(ParsedResume).filter(ParsedResume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume not found: {resume_id}")

        dream_job = db.query(DreamJobDescription).filter(DreamJobDescription.id == dream_job_id).first()
        if not dream_job:
            raise ValueError(f"Dream job not found: {dream_job_id}")

        # Prepare text for LLM
        resume_text = self._prepare_resume_summary(resume)
        dream_job_text = dream_job.description

        # Call LLM for ally type deduction
        ally_types_data = await llm_service.deduce_ally_types(resume_text, dream_job_text)

        # Filter by minimum confidence threshold
        min_confidence = 0.5
        filtered_ally_types = [
            ally for ally in ally_types_data if ally["confidence_score"] >= min_confidence
        ]

        logger.info(f"Deduced {len(filtered_ally_types)} ally types (filtered from {len(ally_types_data)})")

        # Persist to database
        saved_ally_types = []
        for ally_data in filtered_ally_types:
            ally_type = DeducedAllyType(
                dream_job_id=dream_job_id,
                ally_type_name=ally_data["ally_type_name"],
                confidence_score=ally_data["confidence_score"],
                selection_rationale=ally_data["selection_rationale"],
                search_queries=ally_data["search_queries"],
                engagement_strategy=ally_data.get("engagement_strategy", ""),
                rank=ally_data["rank"],
                llm_model=ally_data["llm_model"],
                llm_prompt_version=ally_data["llm_prompt_version"],
            )
            db.add(ally_type)
            saved_ally_types.append(ally_type)

        db.commit()

        return {
            "status": "completed",
            "resume_id": resume_id,
            "dream_job_id": dream_job_id,
            "ally_types_count": len(saved_ally_types),
            "ally_types": [
                {
                    "id": ally.id,
                    "ally_type_name": ally.ally_type_name,
                    "confidence_score": ally.confidence_score,
                    "rank": ally.rank,
                }
                for ally in saved_ally_types
            ],
        }

    def _prepare_resume_summary(self, resume: ParsedResume) -> str:
        """
        Prepare resume summary for LLM input.
        
        Args:
            resume: ParsedResume instance
            
        Returns:
            Formatted resume summary string
        """
        summary_parts = []

        if resume.current_role and resume.current_company:
            summary_parts.append(
                f"Current Position: {resume.current_role} at {resume.current_company}"
            )

        if resume.experience_years:
            summary_parts.append(f"Total Experience: {resume.experience_years} years")

        if resume.skills:
            skills_str = ", ".join(resume.skills[:15])
            summary_parts.append(f"Key Skills: {skills_str}")

        if resume.education:
            summary_parts.append(f"Education: {len(resume.education)} degrees")

        # Add raw text (truncated)
        summary_parts.append(f"\nFull Resume:\n{resume.raw_text[:2000]}")

        return "\n".join(summary_parts)


# Global service instance
ally_deduction_service = AllyDeductionService()
