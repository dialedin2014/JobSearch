"""
Resume parsing service.

Extracts structured data from resume files (PDF, DOCX, TXT).
"""

import PyPDF2
import pdfplumber
import docx
from typing import Dict, Any, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Service for parsing resume files and extracting structured data.

    Supports PDF (PyPDF2 with pdfplumber fallback), DOCX, and TXT formats.
    """

    def __init__(self):
        """Initialize resume parser."""
        self.parser_version = "1.0"

    def extract_text_from_pdf(self, file_path: str) -> tuple[str, float]:
        """
        Extract text from PDF file.

        Tries PyPDF2 first, falls back to pdfplumber if confidence is low.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Try PyPDF2 first
            logger.info(f"Parsing PDF with PyPDF2: {file_path}")
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""

            # Calculate confidence based on text quality
            confidence = self._calculate_confidence(text)

            # If confidence is low, try pdfplumber
            if confidence < 0.7:
                logger.info("Low confidence with PyPDF2, trying pdfplumber")
                text_plumber = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text_plumber += page.extract_text() or ""

                confidence_plumber = self._calculate_confidence(text_plumber)
                if confidence_plumber > confidence:
                    logger.info("pdfplumber gave better results")
                    return text_plumber, confidence_plumber

            return text, confidence

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            # Try pdfplumber as last resort
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text, self._calculate_confidence(text)
            except Exception as e2:
                logger.error(f"pdfplumber also failed: {e2}")
                raise ValueError(f"Failed to parse PDF: {e2}")

    def extract_text_from_docx(self, file_path: str) -> tuple[str, float]:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            logger.info(f"Parsing DOCX: {file_path}")
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            confidence = self._calculate_confidence(text)
            return text, confidence
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise ValueError(f"Failed to parse DOCX: {e}")

    def extract_text_from_txt(self, file_path: str) -> tuple[str, float]:
        """
        Extract text from TXT file.

        Args:
            file_path: Path to TXT file

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            logger.info(f"Reading TXT: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            confidence = self._calculate_confidence(text)
            return text, confidence
        except UnicodeDecodeError:
            # Try different encodings
            try:
                with open(file_path, "r", encoding="latin-1") as file:
                    text = file.read()
                confidence = self._calculate_confidence(text)
                return text, confidence
            except Exception as e:
                logger.error(f"Error reading TXT: {e}")
                raise ValueError(f"Failed to read TXT: {e}")

    def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured data.

        Args:
            file_path: Path to resume file
            file_type: File extension (pdf, docx, txt)

        Returns:
            Dictionary with parsed resume data
        """
        # Extract text based on file type
        if file_type.lower() == "pdf":
            raw_text, confidence = self.extract_text_from_pdf(file_path)
        elif file_type.lower() in ["docx", "doc"]:
            raw_text, confidence = self.extract_text_from_docx(file_path)
        elif file_type.lower() == "txt":
            raw_text, confidence = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Extract structured information
        parsed_data = {
            "raw_text": raw_text,
            "parsing_confidence": confidence,
            "parsed_at": datetime.utcnow(),
            "parser_version": self.parser_version,
            "skills": self._extract_skills(raw_text),
            "achievements": self._extract_achievements(raw_text),
            "work_history": self._extract_work_history(raw_text),
            "education": self._extract_education(raw_text),
            "companies": self._extract_companies(raw_text),
            "keywords": self._extract_keywords(raw_text),
        }

        return parsed_data

    def _calculate_confidence(self, text: str) -> float:
        """
        Calculate parsing confidence based on text quality and extraction success.

        Confidence score 0.0-1.0 based on:
        - Text length and quality
        - Presence of resume sections (experience, education, skills)
        - Successful extraction of key fields
        """
        if not text or len(text.strip()) == 0:
            return 0.0

        # For very short text (< 20 chars), return 0.0
        if len(text) < 20:
            return 0.0

        # For short text (< 50 chars), give minimal confidence only if it looks like resume content
        if len(text) < 50:
            # Check if it has any resume keywords
            resume_indicators = ["experience",
                                 "education", "skills", "work", "degree"]
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in resume_indicators):
                return 0.3
            return 0.0

        # Check for common resume sections
        section_indicators = [
            r"experience", r"education", r"skills", r"work history",
            r"employment", r"degree", r"university", r"college"
        ]

        matches = sum(1 for indicator in section_indicators if re.search(
            indicator, text, re.IGNORECASE))

        # Base confidence on section presence
        base_confidence = min(1.0, (matches / len(section_indicators)) + 0.3)

        # Adjust for text quality
        if len(text) > 1000:  # Substantial content
            base_confidence += 0.1
        if re.search(r'\d{4}', text):  # Contains years (likely dates)
            base_confidence += 0.05
        if re.search(r'@', text):  # Contains email
            base_confidence += 0.05

        return min(1.0, base_confidence)

    def _extract_skills(self, text: str) -> list:
        """
        Extract skills from resume text using pattern matching + NER fallback.

        Returns list of skill strings.
        """
        # Common technical and soft skills
        common_skills = [
            # Programming Languages
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
            # Web Frameworks
            "React", "Angular", "Vue", "Next.js", "Node.js", "FastAPI", "Django", "Flask", "Express", "Spring Boot",
            # Databases
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch",
            # Cloud & DevOps
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins", "GitLab CI", "GitHub Actions",
            # Data & AI
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "scikit-learn",
            "Data Science", "Data Analysis", "Pandas", "NumPy", "Matplotlib", "Jupyter",
            # Tools & Methodologies
            "Git", "Agile", "Scrum", "Kanban", "JIRA", "Confluence", "REST API", "GraphQL", "Microservices",
            # Soft Skills
            "Leadership", "Management", "Communication", "Problem Solving", "Team Collaboration", "Project Management"
        ]

        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills[:30]  # Limit to top 30

    def _extract_achievements(self, text: str) -> list:
        """
        Extract achievements with metrics (bullet points with quantifiable results).

        Returns list of achievement strings with metrics like "30% improvement", "$2M cost reduction".
        """
        achievements = []

        # Look for bullet points (-, *, •) followed by metrics
        bullet_pattern = r'(?:^|\n)[\s]*[-*•]\s*(.+?)(?=\n[-*•]|\n\n|$)'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE | re.DOTALL)

        # Patterns for quantifiable achievements
        metric_patterns = [
            r'\d+%',  # Percentages: 30%, 40%
            r'\$[\d,]+[KMB]?',  # Money: $2M, $500K, $1,000
            # Scale: 10K users, 50 requests
            r'\d+[KMB]?\+?\s*(?:users|customers|clients|requests)',
            # Actions with numbers (more flexible pattern)
            r'(?:increased|reduced|improved|grew|saved|generated|enhanced|optimized|achieved)[\s\w]*\d+',
            r'from\s+\d+\s+to\s+\d+',  # "from 60 to 95"
            r'\d+\s*(?:ms|seconds?|minutes?|hours?)',  # Time: 200ms, 5 seconds
        ]

        for bullet in bullets:
            bullet = bullet.strip()
            # Check if bullet contains metrics
            has_metric = any(re.search(pattern, bullet, re.IGNORECASE)
                             for pattern in metric_patterns)
            if has_metric and len(bullet) > 20:  # Meaningful length
                achievements.append(bullet[:200])  # Limit length

        return achievements[:15]  # Return top 15 achievements

    def _extract_work_history(self, text: str) -> list:
        """
        Extract work history entries with company, title, dates, description.

        Returns list of dicts: [{company, title, start_date, end_date, description}, ...]
        """
        work_history = []

        # Simple pattern matching for common resume formats
        # Look for company names followed by job titles and dates
        # Format: "Company Name" or "Company, Location"
        # Followed by: "Job Title" and dates like "Jan 2020 - Dec 2022"

        # This is a simplified implementation
        # In production, use NLP/NER or LLM for better extraction

        # For now, return empty list - will be enhanced in production
        return work_history

    def _extract_companies(self, text: str) -> list:
        """
        Extract company names for network mapping.

        Returns list of company name strings.
        """
        companies = []

        # Common company indicators
        company_keywords = ["Inc", "LLC", "Ltd",
                            "Corporation", "Corp", "Company", "Co"]

        # Look for capitalized words followed by company indicators
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:' + \
            '|'.join(company_keywords) + r')'
        matches = re.findall(pattern, text)

        companies.extend([match.strip() for match in matches])

        # Also look for well-known tech companies
        known_companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Facebook", "Meta", "Netflix", "Tesla",
            "IBM", "Oracle", "Salesforce", "Adobe", "Intel", "NVIDIA", "Uber", "Airbnb",
            "Twitter", "LinkedIn", "Stripe", "SpaceX", "OpenAI", "Anthropic"
        ]

        text_lower = text.lower()
        for company in known_companies:
            if company.lower() in text_lower:
                companies.append(company)

        # Deduplicate and return
        return list(set(companies))[:20]

    def _extract_education(self, text: str) -> list:
        """
        Extract education information with institution, degree, field, graduation year.

        Returns list of dicts: [{institution, degree, field, graduation_year}, ...]
        """
        education = []

        # Look for degree patterns
        degree_patterns = [
            r'(Bachelor|Master|MBA|PhD|Ph\.D|B\.S\.|M\.S\.|B\.A\.|M\.A.)(?:\s+(?:of|in))?\s+([A-Za-z\s]+)',
            r'(Associate|Diploma)(?:\s+(?:of|in))?\s+([A-Za-z\s]+)'
        ]

        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match[0].strip(),
                    "field": match[1].strip() if len(match) > 1 else "",
                    "institution": "",  # Would extract from context
                    "graduation_year": None  # Would extract from dates
                })

        return education[:5]

    def _extract_keywords(self, text: str) -> list:
        """
        Extract keywords for matching with ally types.

        Returns list of keyword strings extracted from skills, achievements, and work history.
        """
        keywords = []

        # Combine skills as keywords
        skills = self._extract_skills(text)
        keywords.extend(skills)

        # Extract domain-specific keywords
        domain_keywords = [
            # Tech domains
            "artificial intelligence", "machine learning", "data science", "cloud computing",
            "cybersecurity", "blockchain", "IoT", "DevOps", "SaaS", "API",
            # Business domains
            "fintech", "healthcare", "e-commerce", "enterprise software", "mobile apps",
            "sustainability", "renewable energy", "climate tech", "edtech", "biotech",
            # Roles
            "engineering", "product management", "data analysis", "research", "consulting",
            "sales", "marketing", "operations", "strategy", "design"
        ]

        text_lower = text.lower()
        for keyword in domain_keywords:
            if keyword in text_lower:
                keywords.append(keyword.title())

        # Deduplicate and return
        return list(set(keywords))[:50]


# Create singleton instance
resume_parser = ResumeParser()
