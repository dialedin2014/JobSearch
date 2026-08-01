# Job Search Agent (MCP Server)

An autonomous AI agent for job search automation, built using the Model Context Protocol (MCP). This agent can be invoked by GitHub Copilot to perform intelligent job search operations.

## What This Agent Does

This is a **true autonomous agent** that provides:

- **Resume Analysis**: Extract skills, experience, and qualifications from resume files
- **Job Matching**: Calculate compatibility between candidates and job postings
- **Application Strategy**: Generate personalized job search strategies
- **Application Tracking**: Maintain history of job applications and status
- **Cover Letter Generation**: Create tailored cover letters for specific roles

## Installation

### 1. Install Dependencies

```bash
cd .mcp/job-search-agent
pip install -r requirements.txt
```

### 2. Configure GitHub Copilot

Add this agent to your Copilot settings. Edit `%APPDATA%\Code\User\settings.json` (Windows) or `~/.config/Code/User/settings.json` (Linux/Mac):

```json
{
  "github.copilot.chat.mcp": {
    "job-search-agent": {
      "command": "python",
      "args": ["d:\\src\\git\\gh\\di\\JobSearch\\.mcp\\job-search-agent\\server.py"],
      "env": {}
    }
  }
}
```

**Note**: Adjust the path to match your workspace location.

### 3. Restart VS Code

After configuration, restart VS Code for the agent to be available.

## Usage in GitHub Copilot

Once configured, you can invoke the agent in Copilot Chat:

### Example Commands

**Analyze a resume:**
```
@job-search-agent analyze the resume at backend/uploads/my_resume.pdf
```

**Match candidate to job:**
```
@job-search-agent match my resume to this job posting: [paste job description]
```

**Create application strategy:**
```
@job-search-agent create an application strategy for Senior Backend Engineer at TechCorp
```

**Track applications:**
```
@job-search-agent add a new application: Microsoft, Software Engineer, applied status
```

**Generate cover letter:**
```
@job-search-agent write a cover letter for [company] using my resume summary
```

## Available Tools

### 1. `analyze_resume`
- **Input**: Path to resume file (PDF, DOCX, TXT)
- **Output**: Structured data with skills, experience, education
- **Example**: `analyze_resume("backend/uploads/resume.pdf")`

### 2. `match_job_to_resume`
- **Input**: Resume data + job description
- **Output**: Compatibility score, skill gaps, recommendations
- **Example**: `match_job_to_resume(resume, job_desc)`

### 3. `generate_application_strategy`
- **Input**: Target role, candidate profile, company info
- **Output**: Strategy with talking points, interview prep, timeline
- **Example**: `generate_application_strategy("Senior Dev", profile, "Google")`

### 4. `track_application_status`
- **Input**: Action (add/update/list/get), company, role, status
- **Output**: Updated tracking data
- **Example**: `track_application_status("add", "Apple", "iOS Engineer", "applied")`

### 5. `generate_cover_letter`
- **Input**: Job description, resume summary, company, tone
- **Output**: Tailored cover letter draft
- **Example**: `generate_cover_letter(job_desc, summary, "Meta", "enthusiastic")`

## How It Works

This agent uses the **Model Context Protocol (MCP)** to communicate with GitHub Copilot:

1. **Tool Registration**: Agent declares available tools and their schemas
2. **Invocation**: Copilot calls tools based on user queries
3. **Execution**: Agent processes requests autonomously
4. **Response**: Returns structured data or generated content

Unlike simple prompt files (`.prompt.md`), this is a **stateful, autonomous agent** that can:
- Make decisions based on context
- Maintain persistent state (application tracking)
- Perform complex multi-step operations
- Integrate with external systems (if extended)

## Extending the Agent

To add new capabilities:

1. **Add tool definition** to `list_tools()`
2. **Implement handler** function
3. **Add routing** in `call_tool()`

Example:
```python
@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="search_job_boards",
            description="Search multiple job boards for matching positions",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {"type": "string"},
                    "location": {"type": "string"}
                }
            }
        )
    ]
```

## Integration with JobSearch Backend

This agent can be enhanced to integrate with the existing FastAPI backend:

- Call `/api/resume/parse` for real resume parsing
- Use `/api/jobs/match` for production matching algorithms
- Leverage existing embedding service and LLM service
- Store tracking data in the PostgreSQL database

## Troubleshooting

**Agent not appearing in Copilot:**
- Check settings.json syntax is valid
- Verify path to server.py is correct (use absolute path)
- Restart VS Code completely

**Tool execution errors:**
- Check Python dependencies are installed
- Verify file paths are relative to workspace root
- Review error messages in Copilot output

**Performance issues:**
- Enable debug logging in MCP settings
- Consider async operations for I/O-heavy tasks
- Cache frequently accessed data

## Architecture

```
User Request → GitHub Copilot Chat
                     ↓
              MCP Protocol
                     ↓
         Job Search Agent (this)
                     ↓
         ┌───────────┴───────────┐
         ↓                       ↓
   Tool Execution        State Management
         ↓                       ↓
    Resume Analysis      applications.json
    Job Matching
    Strategy Generation
```

## Future Enhancements

- [ ] Real LLM integration (Claude, GPT-4)
- [ ] Web scraping for live job postings
- [ ] Email integration for follow-ups
- [ ] Calendar integration for interview scheduling
- [ ] LinkedIn API integration
- [ ] Resume builder/formatter
- [ ] Interview question generator
- [ ] Salary negotiation advisor

## License

Part of the JobSearch project. See root LICENSE file.
