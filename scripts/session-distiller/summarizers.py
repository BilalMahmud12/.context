#!/usr/bin/env python3
"""
AI Summarizers for AgentShell Session Distillation

Uses Anthropic API to generate coherent session summaries.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass

try:
    from anthropic import Anthropic
except ImportError:
    print("Error: anthropic package not installed")
    print("Install with: pip install anthropic")
    exit(1)

from extractors import SessionData


@dataclass
class SummarizedSession:
    """Summarized session data ready for template rendering."""
    # Metadata
    session_id: str
    title: str
    date: str
    duration: str
    branch: str
    agent: str
    model: str
    project_name: str

    # AI-generated summaries
    summary_paragraph: str
    user_requests: str
    starting_state: str
    narrative: str
    key_decisions: List[Dict[str, str]]
    blockers: List[Dict[str, str]]
    code_snippets: List[Dict[str, str]]
    search_keywords: List[str]

    # Extracted data
    files_created: List[str]
    files_modified: List[str]
    files_deleted: List[str]
    files_read: List[str]
    commands: List[Dict[str, str]]
    related_tasks: List[str]

    # References
    raw_session_path: str


def prefilter_session_data(session: SessionData) -> str:
    """
    Pre-filter session data to reduce size before AI processing.

    Removes unnecessary data and truncates long outputs.
    Returns a formatted string suitable for AI summarization.
    """
    lines = []

    lines.append(f"# Session: {session.title or session.session_id}")
    lines.append(f"Project: {session.project_name}")
    lines.append(f"Branch: {session.branch}")
    lines.append(f"Duration: {session.duration_minutes} minutes")
    lines.append(f"Model: {session.model}")
    lines.append("")

    # Add conversation flow
    lines.append("## Conversation\n")

    for msg in session.messages:
        role = msg.role.upper()
        timestamp = msg.timestamp.strftime("%H:%M:%S")

        lines.append(f"[{timestamp}] {role}:")

        if msg.content:
            # Truncate very long content
            content = msg.content
            if len(content) > 2000:
                content = content[:1000] + "\n[... truncated ...]\n" + content[-1000:]
            lines.append(content)

        if msg.tool_calls:
            lines.append("\nTool calls:")
            for tool in msg.tool_calls:
                lines.append(f"  - {tool['name']}: {tool['input']}")

        if msg.tool_results:
            lines.append("\nTool results:")
            for result in msg.tool_results:
                output = result.get('content', '')
                if isinstance(output, str) and len(output) > 500:
                    output = output[:250] + "\n[... truncated ...]\n" + output[-250:]
                lines.append(f"  - {output}")

        lines.append("")

    # Add file operations summary
    if session.files_modified or session.files_created:
        lines.append("## Files Changed\n")
        if session.files_created:
            lines.append("Created:")
            for f in session.files_created:
                lines.append(f"  - {f}")
        if session.files_modified:
            lines.append("Modified:")
            for f in session.files_modified:
                lines.append(f"  - {f}")
        lines.append("")

    # Add commands
    if session.commands:
        lines.append("## Commands Run\n")
        for cmd in session.commands:
            lines.append(f"$ {cmd.command}")
            if cmd.description:
                lines.append(f"  # {cmd.description}")
            if cmd.output:
                output = cmd.output
                if len(output) > 500:
                    output = output[:250] + "\n[... truncated ...]\n" + output[-250:]
                lines.append(f"Output: {output}")
            lines.append("")

    return '\n'.join(lines)


def chunk_text(text: str, max_chunk_size: int = 40000) -> List[str]:
    """
    Split text into chunks suitable for AI processing.

    Args:
        text: Text to chunk
        max_chunk_size: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    # Simple chunking by splitting on double newlines
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para)

        if current_size + para_size > max_chunk_size and current_chunk:
            # Save current chunk and start new one
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size
        else:
            current_chunk.append(para)
            current_size += para_size

    # Add final chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def summarize_chunk(client: Anthropic, chunk: str, chunk_num: int, total_chunks: int) -> str:
    """
    Summarize a single chunk of session data using Claude Haiku.

    Args:
        client: Anthropic client
        chunk: Text chunk to summarize
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks

    Returns:
        Summary text
    """
    prompt = f"""Summarize this Claude Code session excerpt (part {chunk_num} of {total_chunks}).

Extract and preserve:
1. What the user requested or asked about
2. What actions were taken (commands, file edits, tool use)
3. Key decisions made and their reasoning
4. Problems or blockers encountered
5. Important technical details (file paths, command outputs, code snippets)

Be concise but technical. Focus on WHAT happened, not HOW to do it.
Preserve specific file paths, commands, and error messages exactly.

SESSION EXCERPT:
{chunk}

Provide a structured summary with clear sections."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    except Exception as e:
        return f"Error summarizing chunk {chunk_num}: {e}"


def synthesize_summary(client: Anthropic, session: SessionData, chunk_summaries: List[str]) -> Dict[str, Any]:
    """
    Synthesize chunk summaries into a cohesive session summary.

    Uses Claude Sonnet for higher quality synthesis.

    Args:
        client: Anthropic client
        session: Original session data
        chunk_summaries: List of chunk summaries from Haiku

    Returns:
        Dictionary with all summary components
    """
    # Build context from session metadata
    files_context = ""
    if session.files_created:
        files_context += f"\nFiles created: {', '.join(session.files_created)}"
    if session.files_modified:
        files_context += f"\nFiles modified: {', '.join(session.files_modified)}"

    commands_context = ""
    if session.commands:
        commands_context = "\nCommands run:\n"
        for cmd in session.commands[:10]:  # Limit to first 10
            commands_context += f"  - {cmd.command}\n"

    prompt = f"""Create a comprehensive session summary from these extracted sections.

SESSION METADATA:
- Session ID: {session.session_id}
- Project: {session.project_name}
- Branch: {session.branch}
- Duration: {session.duration_minutes} minutes
- Model: {session.model}
{files_context}
{commands_context}

EXTRACTED SECTIONS:
{chr(10).join(f'=== Part {i+1} ==={chr(10)}{summary}' for i, summary in enumerate(chunk_summaries))}

Generate a detailed session summary with these sections:

1. SUMMARY_PARAGRAPH: One concise paragraph (3-5 sentences) summarizing the entire session.

2. USER_REQUESTS: What did the user ask for? What were their goals?

3. STARTING_STATE: What was the state of the project when the session began?

4. NARRATIVE: A detailed chronological narrative of what happened. Include technical details, decisions made, and outcomes.

5. KEY_DECISIONS: List of important decisions made (format: Decision | Reasoning | Impact). Minimum 3, maximum 8.

6. BLOCKERS: Problems encountered and how they were resolved (format: Blocker | Resolution | Lesson). Include if any occurred.

7. CODE_SNIPPETS: Important code changes or snippets worth highlighting (format: Title | Language | Code | Explanation). Include 2-4 most significant ones.

8. SEARCH_KEYWORDS: 10-15 keywords for future discovery (comma-separated). Include: technologies, file names, concepts, actions.

9. RELATED_TASKS: Any task files mentioned (e.g., "001", "002-reference-tables").

Format your response as JSON:
{{
  "summary_paragraph": "...",
  "user_requests": "...",
  "starting_state": "...",
  "narrative": "...",
  "key_decisions": [
    {{"decision": "...", "reasoning": "...", "impact": "..."}},
    ...
  ],
  "blockers": [
    {{"blocker": "...", "resolution": "...", "lesson": "..."}},
    ...
  ],
  "code_snippets": [
    {{"title": "...", "language": "...", "code": "...", "explanation": "..."}},
    ...
  ],
  "search_keywords": ["keyword1", "keyword2", ...],
  "related_tasks": ["001", "002", ...]
}}

Be thorough and detailed. Target 2000-3000 words for the narrative."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        import json
        result_text = response.content[0].text

        # Extract JSON from markdown code blocks if present
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()

        return json.loads(result_text)

    except Exception as e:
        # Return minimal structure if synthesis fails
        return {
            "summary_paragraph": f"Session summary generation failed: {e}",
            "user_requests": "See raw session",
            "starting_state": "Unknown",
            "narrative": "Synthesis failed. See chunk summaries above.",
            "key_decisions": [],
            "blockers": [],
            "code_snippets": [],
            "search_keywords": [session.project_name, session.branch],
            "related_tasks": []
        }


def summarize_session(session: SessionData, use_ai: bool = True) -> SummarizedSession:
    """
    Main function to summarize a session.

    Args:
        session: Extracted session data
        use_ai: Whether to use AI for summarization (default: True)

    Returns:
        SummarizedSession with all components filled
    """
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key and use_ai:
        print("Warning: ANTHROPIC_API_KEY not set. AI summarization disabled.")
        use_ai = False

    if use_ai:
        client = Anthropic(api_key=api_key)

        # Step 1: Pre-filter
        print("  Pre-filtering session data...")
        filtered = prefilter_session_data(session)
        print(f"  Filtered to {len(filtered)} characters")

        # Step 2: Chunk and summarize
        chunks = chunk_text(filtered, max_chunk_size=40000)
        print(f"  Split into {len(chunks)} chunks")

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"  Summarizing chunk {i+1}/{len(chunks)} with Haiku...")
            summary = summarize_chunk(client, chunk, i+1, len(chunks))
            chunk_summaries.append(summary)

        # Step 3: Synthesize
        print("  Synthesizing final summary with Sonnet...")
        synthesis = synthesize_summary(client, session, chunk_summaries)

    else:
        # No AI - return template structure
        synthesis = {
            "summary_paragraph": session.title or "Session summary (AI disabled)",
            "user_requests": "See raw session",
            "starting_state": f"Branch: {session.branch}",
            "narrative": "AI summarization was disabled. See extracted data below.",
            "key_decisions": [],
            "blockers": [],
            "code_snippets": [],
            "search_keywords": [session.project_name, session.branch],
            "related_tasks": []
        }

    # Build command list
    commands_list = []
    for cmd in session.commands:
        commands_list.append({
            'command': cmd.command,
            'description': cmd.description,
            'output': cmd.output[:1000] if cmd.output else ''  # Truncate output
        })

    # Determine agent name
    agent_name = "M-O" if "sonnet" in session.model.lower() else "Aang" if "opus" in session.model.lower() else "Unknown"

    # Build summarized session
    summarized = SummarizedSession(
        session_id=session.session_id,
        title=session.title or "Untitled Session",
        date=session.start_time.strftime("%Y-%m-%d"),
        duration=f"{session.duration_minutes} minutes",
        branch=session.branch,
        agent=agent_name,
        model=session.model,
        project_name=session.project_name,

        summary_paragraph=synthesis['summary_paragraph'],
        user_requests=synthesis['user_requests'],
        starting_state=synthesis['starting_state'],
        narrative=synthesis['narrative'],
        key_decisions=synthesis['key_decisions'],
        blockers=synthesis['blockers'],
        code_snippets=synthesis['code_snippets'],
        search_keywords=synthesis['search_keywords'],

        files_created=session.files_created,
        files_modified=session.files_modified,
        files_deleted=session.files_deleted,
        files_read=session.files_read,
        commands=commands_list,
        related_tasks=synthesis['related_tasks'],

        raw_session_path=f"~/.claude/projects/*/{ session.session_id}.jsonl"
    )

    return summarized
