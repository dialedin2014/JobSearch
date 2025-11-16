"""
Unit tests for resume_parser.py - Resume text extraction and parsing.

Tests cover:
- PDF text extraction (PyPDF2 + pdfplumber fallback)
- DOCX text extraction
- TXT text extraction with encoding handling
- Skills extraction
- Achievements extraction with metrics
- Confidence calculation
- Edge cases and error handling

Target: ≥85% coverage per T022c requirement
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.resume_parser import ResumeParser, resume_parser


@pytest.mark.unit
@pytest.mark.resume
class TestResumeTextExtraction:
    """Test text extraction from different file formats."""

    def test_extract_text_from_txt_simple(self, tmp_path):
        """Test extracting text from simple TXT file."""
        # Create temporary TXT file
        txt_file = tmp_path / "resume.txt"
        content = """John Doe
        Software Engineer
        Experience with Python, Java, and AWS
        Education: BS Computer Science
        """
        txt_file.write_text(content)

        parser = ResumeParser()
        text, confidence = parser.extract_text_from_txt(str(txt_file))

        assert "John Doe" in text
        assert "Python" in text
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_extract_text_from_txt_utf8(self, tmp_path):
        """Test extracting text from UTF-8 encoded file."""
        txt_file = tmp_path / "resume_utf8.txt"
        content = "Software Engineer 🚀\nSkills: Python, ML"
        txt_file.write_text(content, encoding="utf-8")

        parser = ResumeParser()
        text, confidence = parser.extract_text_from_txt(str(txt_file))

        assert "Python" in text
        assert confidence > 0.0

    def test_extract_text_from_txt_latin1_fallback(self, tmp_path):
        """Test extracting text with latin-1 encoding fallback."""
        txt_file = tmp_path / "resume_latin1.txt"
        # Write with latin-1 encoding
        with open(txt_file, "w", encoding="latin-1") as f:
            f.write("Résumé - Software Engineer\nExperience")

        parser = ResumeParser()
        # Should handle latin-1 fallback
        text, confidence = parser.extract_text_from_txt(str(txt_file))

        assert "Experience" in text

    @patch('src.services.resume_parser.pdfplumber')
    @patch('src.services.resume_parser.PyPDF2')
    def test_extract_text_from_pdf_success(self, mock_pypdf2, mock_pdfplumber, tmp_path):
        """Test successful PDF text extraction with PyPDF2."""
        # Mock PyPDF2 PdfReader
        mock_page = Mock()
        mock_page.extract_text.return_value = """John Doe
        Software Engineer
        Experience: 5 years in Python, FastAPI
        Education: BS Computer Science
        Skills: Python, Docker, AWS
        """

        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader_instance

        # Also mock pdfplumber in case of fallback
        mock_pdf_instance = Mock()
        mock_pdf_page = Mock()
        mock_pdf_page.extract_text.return_value = mock_page.extract_text.return_value
        mock_pdf_instance.pages = [mock_pdf_page]
        mock_pdf_instance.__enter__ = Mock(return_value=mock_pdf_instance)
        mock_pdf_instance.__exit__ = Mock(return_value=False)
        mock_pdfplumber.open.return_value = mock_pdf_instance

        # Create dummy PDF file
        pdf_file = tmp_path / "resume.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 dummy")

        parser = ResumeParser()
        text, confidence = parser.extract_text_from_pdf(str(pdf_file))

        assert "Python" in text
        assert "FastAPI" in text
        assert confidence > 0.5  # Should have decent confidence with keywords

    @patch('PyPDF2.PdfReader')
    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_fallback_to_pdfplumber(self, mock_pdfplumber, mock_pypdf2, tmp_path):
        """Test PDF extraction falls back to pdfplumber when PyPDF2 gives low confidence."""
        # Mock PyPDF2 with poor extraction
        mock_pypdf2_page = Mock()
        mock_pypdf2_page.extract_text.return_value = "gibberish text"
        mock_pypdf2_instance = Mock()
        mock_pypdf2_instance.pages = [mock_pypdf2_page]
        mock_pypdf2.return_value = mock_pypdf2_instance

        # Mock pdfplumber with good extraction
        mock_plumber_page = Mock()
        mock_plumber_page.extract_text.return_value = """John Doe
        Experience: Software Engineer
        Education: BS Computer Science
        Skills: Python, Java, AWS
        """
        mock_plumber_pdf = Mock()
        mock_plumber_pdf.pages = [mock_plumber_page]
        mock_plumber_pdf.__enter__ = Mock(return_value=mock_plumber_pdf)
        mock_plumber_pdf.__exit__ = Mock(return_value=False)
        mock_pdfplumber.return_value = mock_plumber_pdf

        pdf_file = tmp_path / "resume.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 dummy")

        parser = ResumeParser()
        text, confidence = parser.extract_text_from_pdf(str(pdf_file))

        # Should use pdfplumber result
        assert "Experience" in text
        assert "Skills" in text

    @patch('docx.Document')
    def test_extract_text_from_docx_success(self, mock_docx_doc, tmp_path):
        """Test successful DOCX text extraction."""
        # Mock DOCX document
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "John Doe - Software Engineer"
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "Experience: Python, FastAPI, Docker"
        mock_paragraph3 = Mock()
        mock_paragraph3.text = "Education: BS Computer Science"

        mock_doc_instance = Mock()
        mock_doc_instance.paragraphs = [
            mock_paragraph1, mock_paragraph2, mock_paragraph3]
        mock_docx_doc.return_value = mock_doc_instance

        docx_file = tmp_path / "resume.docx"
        docx_file.write_bytes(b"PK dummy docx")  # Dummy DOCX

        parser = ResumeParser()
        text, confidence = parser.extract_text_from_docx(str(docx_file))

        assert "John Doe" in text
        assert "Python" in text
        assert confidence > 0.0

    @patch('docx.Document')
    def test_extract_text_from_docx_error_handling(self, mock_docx_doc, tmp_path):
        """Test DOCX extraction error handling."""
        mock_docx_doc.side_effect = Exception("Corrupt DOCX file")

        docx_file = tmp_path / "corrupt.docx"
        docx_file.write_bytes(b"corrupt data")

        parser = ResumeParser()

        with pytest.raises(ValueError, match="Failed to parse DOCX"):
            parser.extract_text_from_docx(str(docx_file))


@pytest.mark.unit
@pytest.mark.resume
class TestConfidenceCalculation:
    """Test confidence score calculation."""

    def test_calculate_confidence_high_quality(self):
        """Test confidence calculation for high-quality resume text."""
        parser = ResumeParser()
        text = """
        John Doe - Software Engineer
        
        Experience:
        Senior Engineer at TechCorp
        - Led team of 5 engineers
        
        Education:
        BS Computer Science, University of Tech
        
        Skills:
        Python, Java, AWS, Docker
        
        Work History:
        2020-2023: Senior Engineer
        2018-2020: Software Engineer
        """

        confidence = parser._calculate_confidence(text)

        # Should have high confidence with multiple indicators
        assert confidence > 0.7
        assert confidence <= 1.0

    def test_calculate_confidence_low_quality(self):
        """Test confidence calculation for low-quality text."""
        parser = ResumeParser()
        text = "Some random text without resume keywords"

        confidence = parser._calculate_confidence(text)

        # Should have lower confidence
        assert confidence < 0.6

    def test_calculate_confidence_empty_text(self):
        """Test confidence calculation for empty text."""
        parser = ResumeParser()

        assert parser._calculate_confidence("") == 0.0
        assert parser._calculate_confidence("short") == 0.0

    def test_calculate_confidence_minimal_resume(self):
        """Test confidence with minimal resume containing some keywords."""
        parser = ResumeParser()
        text = """
        Work experience at Company X
        Education: Some College
        """

        confidence = parser._calculate_confidence(text)

        assert 0.0 < confidence < 0.7


@pytest.mark.unit
@pytest.mark.resume
class TestSkillsExtraction:
    """Test skill extraction from resume text."""

    def test_extract_skills_common_tech_skills(self):
        """Test extracting common technical skills."""
        parser = ResumeParser()
        text = """
        Skills: Python, JavaScript, React, Docker, AWS, PostgreSQL
        Experience with Machine Learning and Data Science
        """

        skills = parser._extract_skills(text)

        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills
        assert "Docker" in skills
        assert "AWS" in skills
        assert "Machine Learning" in skills

    def test_extract_skills_case_insensitive(self):
        """Test that skill extraction is case-insensitive."""
        parser = ResumeParser()
        text = "PYTHON, javascript, React, aws"

        skills = parser._extract_skills(text)

        assert "Python" in skills
        assert "JavaScript" in skills
        assert "React" in skills
        assert "AWS" in skills

    def test_extract_skills_no_skills_found(self):
        """Test extraction when no skills are found."""
        parser = ResumeParser()
        text = "Random text with no technical skills mentioned"

        skills = parser._extract_skills(text)

        # Might find some soft skills but should be minimal
        assert isinstance(skills, list)

    def test_extract_skills_limits_to_30(self):
        """Test that skills extraction limits to 30 skills."""
        parser = ResumeParser()
        # Text with many skills
        text = """Python JavaScript Java C++ Go Rust Ruby PHP Swift Kotlin
        React Angular Vue Django Flask FastAPI Spring Express
        PostgreSQL MySQL MongoDB Redis Cassandra Elasticsearch
        Docker Kubernetes AWS Azure GCP Terraform Jenkins
        Machine Learning Deep Learning NLP Computer Vision
        Git Agile Scrum Leadership Management Communication
        """

        skills = parser._extract_skills(text)

        assert len(skills) <= 30


@pytest.mark.unit
@pytest.mark.resume
class TestAchievementsExtraction:
    """Test achievement extraction with metrics."""

    def test_extract_achievements_with_percentages(self):
        """Test extracting achievements with percentage metrics."""
        parser = ResumeParser()
        text = """
        - Improved system performance by 40% through code optimization
        - Reduced server costs by 30% by migrating to AWS
        - Increased user engagement by 25%
        """

        achievements = parser._extract_achievements(text)

        assert len(achievements) >= 2
        assert any("40%" in ach for ach in achievements)
        assert any("30%" in ach for ach in achievements)

    def test_extract_achievements_with_money(self):
        """Test extracting achievements with monetary metrics."""
        parser = ResumeParser()
        text = """
        - Saved $2M annually by optimizing infrastructure
        - Generated $500K in additional revenue
        - Reduced costs by $100,000 per year
        """

        achievements = parser._extract_achievements(text)

        assert len(achievements) >= 2
        assert any("$2M" in ach or "$500K" in ach for ach in achievements)

    def test_extract_achievements_with_scale(self):
        """Test extracting achievements with user/scale metrics."""
        parser = ResumeParser()
        text = """
        - Built platform serving 10K+ users daily
        - Managed team supporting 5M customers
        - Led migration affecting 100K users
        """

        achievements = parser._extract_achievements(text)

        assert len(achievements) >= 2
        assert any("users" in ach.lower() or "customers" in ach.lower()
                   for ach in achievements)

    def test_extract_achievements_with_action_verbs(self):
        """Test extracting achievements with action verbs and numbers."""
        parser = ResumeParser()
        text = """
        - Increased system throughput by 50 requests/second
        - Reduced latency by 200ms on average
        - Improved code coverage from 60 to 95 percent
        """

        achievements = parser._extract_achievements(text)

        assert len(achievements) >= 1

    def test_extract_achievements_filters_short_bullets(self):
        """Test that short bullet points without metrics are filtered."""
        parser = ResumeParser()
        text = """
        - Did stuff
        - Worked on projects
        - Improved system performance by 40% through optimization
        - Helped team
        """

        achievements = parser._extract_achievements(text)

        # Should only extract the one with metrics
        assert all(len(ach) > 20 for ach in achievements)

    def test_extract_achievements_limits_to_15(self):
        """Test that achievements are limited to top 15."""
        parser = ResumeParser()
        # Create text with many achievements
        bullets = [
            f"- Improved metric by {i}% through optimization" for i in range(20, 50)]
        text = "\n".join(bullets)

        achievements = parser._extract_achievements(text)

        assert len(achievements) <= 15

    def test_extract_achievements_no_achievements(self):
        """Test extraction when no achievements with metrics are found."""
        parser = ResumeParser()
        text = """
        Worked at company
        Did various tasks
        Helped with projects
        """

        achievements = parser._extract_achievements(text)

        assert isinstance(achievements, list)
        # Might be empty or have very few
        assert len(achievements) <= 3


@pytest.mark.unit
@pytest.mark.resume
class TestResumeParserIntegration:
    """Test full parse_resume workflow."""

    @patch.object(ResumeParser, 'extract_text_from_txt')
    def test_parse_resume_txt_format(self, mock_extract_txt, tmp_path):
        """Test parsing TXT resume file."""
        mock_extract_txt.return_value = (
            """John Doe
            Experience: Python, FastAPI, Docker
            - Improved performance by 40%
            Education: BS Computer Science
            Skills: Python, AWS, React
            """,
            0.8
        )

        txt_file = tmp_path / "resume.txt"
        txt_file.write_text("dummy content")

        parser = ResumeParser()
        result = parser.parse_resume(str(txt_file), "txt")

        assert "raw_text" in result
        assert result["parsing_confidence"] == 0.8
        assert "parser_version" in result
        assert isinstance(result["skills"], list)
        assert isinstance(result["achievements"], list)
        assert "parsed_at" in result

    @patch.object(ResumeParser, 'extract_text_from_pdf')
    def test_parse_resume_pdf_format(self, mock_extract_pdf, tmp_path):
        """Test parsing PDF resume file."""
        mock_extract_pdf.return_value = (
            """Senior Software Engineer
            Experience with Python, Java, AWS
            Education: MS Computer Science
            """,
            0.75
        )

        pdf_file = tmp_path / "resume.pdf"
        pdf_file.write_bytes(b"dummy pdf")

        parser = ResumeParser()
        result = parser.parse_resume(str(pdf_file), "pdf")

        assert result["parsing_confidence"] == 0.75
        assert "skills" in result
        assert "education" in result

    def test_parse_resume_unsupported_format(self, tmp_path):
        """Test parsing with unsupported file format raises error."""
        bad_file = tmp_path / "resume.xyz"
        bad_file.write_text("content")

        parser = ResumeParser()

        with pytest.raises(ValueError, match="Unsupported file type"):
            parser.parse_resume(str(bad_file), "xyz")


@pytest.mark.unit
@pytest.mark.resume
class TestResumeParserInstance:
    """Test the module-level resume_parser instance."""

    def test_resume_parser_instance_exists(self):
        """Test that resume_parser singleton exists."""
        assert resume_parser is not None
        assert isinstance(resume_parser, ResumeParser)
        assert resume_parser.parser_version == "1.0"
