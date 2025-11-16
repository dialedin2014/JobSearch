"""
LLM service for ally type deduction using Claude 3 Sonnet.

This module provides high-level LLM operations with structured prompts.
"""

from typing import Dict, Any, List, Optional
import json
import logging
import hashlib
from datetime import datetime, timedelta
from src.integrations.anthropic_client import anthropic_client

logger = logging.getLogger(__name__)

# In-memory cache for LLM responses (in production, use Redis)
# Structure: {cache_key: {"response": data, "timestamp": datetime}}
_llm_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_HOURS = 24

# Prompt template for ally type deduction
ALLY_DEDUCTION_PROMPT = """You are an expert career advisor analyzing a professional's resume and dream job to identify the most valuable types of professional allies they should connect with.

**Resume Summary:**
{resume_text}

**Dream Job Description:**
{dream_job_text}

**Task:** Based on this professional's current background and career aspirations, deduce 3-7 specific types of professional allies who would be most valuable for achieving their dream job. For each ally type, provide:

1. **Ally Type Name**: A clear, specific descriptor (e.g., "AI/ML Technical Leaders in Healthcare", "Senior Product Managers at B2B SaaS Companies")

2. **Confidence Score**: A score from 0.0 to 1.0 indicating how confident you are that this ally type would be valuable

3. **Selection Rationale**: Explain why this ally type would help bridge the gap between current state and dream job

4. **Search Queries**: Provide platform-specific search queries:
   - GitHub: Search query to find relevant users (use language, location, topic filters)
   - Twitter: Keywords and hashtags to find relevant professionals
   - LinkedIn: Job titles, companies, or industries to search

5. **Engagement Strategy**: Brief guidance on how to approach and engage with this ally type

**Output Format:** Return a valid JSON array with this structure:

```json
[
  {{
    "ally_type_name": "AI/ML Technical Leaders in Healthcare",
    "confidence_score": 0.85,
    "selection_rationale": "Given your background in software engineering and goal to transition into AI healthcare applications, connecting with technical leaders who have successfully made this transition will provide mentorship on required skills, common pitfalls, and industry insights.",
    "search_queries": {{
      "github": "location:USA language:Python topic:healthcare topic:machine-learning followers:>100",
      "twitter": "#AIinHealthcare #HealthTech #MachineLearning healthcare AND (AI OR ML)",
      "linkedin": "AI Engineer Healthcare OR Machine Learning Healthcare OR Data Scientist Healthcare"
    }},
    "engagement_strategy": "Start by engaging with their open-source healthcare ML projects, share insights on their blog posts about AI in healthcare, then reach out for informational interviews focusing on technical transition challenges."
  }}
]
```

**Guidelines:**
- Prioritize ally types that address specific skill gaps or experience needs
- Consider both technical mentors and industry insiders
- Ensure ally types are specific enough to search for effectively
- Confidence scores should reflect realistic value (most should be 0.6-0.9)
- Search queries should be actionable and likely to find 5+ relevant people
- Rank by importance (most critical allies first)

**Important:** Return ONLY the JSON array, no additional text or explanation.
"""


class LLMService:
    """
    Service for LLM operations using Claude 3 Sonnet.

    Provides high-level methods for ally type deduction and other
    LLM-powered features with response caching.
    """

    def __init__(self):
        """Initialize LLM service."""
        self.client = anthropic_client
        self.prompt_version = "1.0"

    def _generate_cache_key(self, resume_text: str, dream_job_text: str) -> str:
        """
        Generate a cache key from resume and dream job text.

        Args:
            resume_text: Resume text
            dream_job_text: Dream job description

        Returns:
            SHA256 hash of combined texts
        """
        combined = f"{resume_text[:3000]}||{dream_job_text[:1000]}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get response from cache if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached response or None if not found/expired
        """
        if cache_key not in _llm_cache:
            return None

        cached = _llm_cache[cache_key]
        age = datetime.utcnow() - cached["timestamp"]

        if age > timedelta(hours=CACHE_TTL_HOURS):
            # Cache expired, remove it
            del _llm_cache[cache_key]
            logger.info(f"Cache expired for key {cache_key[:16]}...")
            return None

        logger.info(f"Cache hit for key {cache_key[:16]}... (age: {age})")
        return cached["response"]

    def _save_to_cache(self, cache_key: str, response: List[Dict[str, Any]]) -> None:
        """
        Save response to cache.

        Args:
            cache_key: Cache key
            response: Response to cache
        """
        _llm_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.utcnow(),
        }
        logger.info(f"Cached response for key {cache_key[:16]}...")

    async def deduce_ally_types(
        self, resume_text: str, dream_job_text: str
    ) -> List[Dict[str, Any]]:
        """
        Deduce professional ally types from resume and dream job.

        Uses caching to reduce API costs. Cache TTL is 24 hours.

        Args:
            resume_text: Full resume text or summary
            dream_job_text: Dream job description

        Returns:
            List of ally type dictionaries with confidence scores and metadata

        Raises:
            ValueError: If LLM response cannot be parsed
        """
        # Check cache first
        cache_key = self._generate_cache_key(resume_text, dream_job_text)
        cached_response = self._get_from_cache(cache_key)

        if cached_response is not None:
            logger.info("Returning cached ally type deduction (cost savings: ~$0.01-0.03)")
            return cached_response

        logger.info("Deducing ally types with Claude 3 Sonnet (cache miss)")

        # Prepare prompt
        prompt = ALLY_DEDUCTION_PROMPT.format(
            resume_text=resume_text[:3000],  # Limit to 3000 chars
            dream_job_text=dream_job_text[:1000],  # Limit to 1000 chars
        )

        try:
            # Call Claude API
            response = await self.client.create_message(
                prompt=prompt,
                system_message="You are an expert career advisor specializing in professional networking strategy.",
                max_tokens=4096,
                temperature=0.7,
            )

            # Parse JSON response
            content = response["content"].strip()

            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            ally_types = json.loads(content)

            # Validate and enhance response
            validated_ally_types = []
            for i, ally in enumerate(ally_types):
                # Ensure required fields
                if not all(
                    key in ally
                    for key in [
                        "ally_type_name",
                        "confidence_score",
                        "selection_rationale",
                        "search_queries",
                    ]
                ):
                    logger.warning(f"Skipping invalid ally type at index {i}")
                    continue

                # Add metadata
                ally["rank"] = i + 1
                ally["llm_model"] = response.get(
                    "model", "claude-sonnet-4-5-20250929")
                ally["llm_prompt_version"] = self.prompt_version

                # Ensure engagement_strategy exists
                if "engagement_strategy" not in ally:
                    ally["engagement_strategy"] = "Connect and engage authentically"

                validated_ally_types.append(ally)

            logger.info(
                f"Successfully deduced {len(validated_ally_types)} ally types")

            # Cache the response
            self._save_to_cache(cache_key, validated_ally_types)

            return validated_ally_types

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {content}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise

    async def generate_clarification_questions(
        self, resume_text: str, parsing_confidence: float
    ) -> List[str]:
        """
        Generate clarification questions for low-confidence resume parsing.

        Args:
            resume_text: Parsed resume text
            parsing_confidence: Confidence score from parser

        Returns:
            List of clarification questions for the user
        """
        if parsing_confidence >= 0.7:
            return []

        prompt = f"""The following resume was parsed with low confidence ({parsing_confidence:.2f}). 
Generate 3-5 specific questions to ask the user to clarify missing or unclear information:

**Resume Text:**
{resume_text[:2000]}

Return a JSON array of question strings. Focus on:
- Current job title and company
- Years of experience
- Key technical skills
- Education background
- Career goals

Format: ["Question 1?", "Question 2?", ...]
"""

        try:
            response = await self.client.create_message(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5,
            )

            content = response["content"].strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            questions = json.loads(content)
            return questions[:5]  # Limit to 5 questions

        except Exception as e:
            logger.error(f"Error generating clarification questions: {e}")
            # Return default questions
            return [
                "What is your current job title and company?",
                "How many years of professional experience do you have?",
                "What are your top 5 technical skills?",
            ]


# Global service instance
llm_service = LLMService()
