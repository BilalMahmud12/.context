#!/usr/bin/env python3
"""
Session Data Extractors for AgentShell

Parses Claude Code JSONL session files and extracts structured data.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class Message:
    """A single message in the conversation."""
    uuid: str
    role: str  # 'user' or 'assistant'
    content: str  # Text content
    timestamp: datetime
    thinking: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ToolCall:
    """A tool invocation during the session."""
    name: str  # Tool name (Read, Edit, Bash, etc.)
    input: Dict[str, Any]  # Tool parameters
    output: Optional[str] = None  # Tool result
    timestamp: datetime = None
    message_uuid: str = None


@dataclass
class Command:
    """A bash command executed during the session."""
    command: str
    description: str
    output: str
    timestamp: datetime
    message_uuid: str


@dataclass
class SessionData:
    """Complete extracted session data."""
    session_id: str
    project_name: str
    project_path: str
    branch: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int

    # Session metadata
    title: str = ""
    model: str = ""
    slug: str = ""

    # Conversation
    messages: List[Message] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    commands: List[Command] = field(default_factory=list)

    # File operations
    files_read: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)

    # Tracking
    errors: List[str] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)


def extract_text_content(content_blocks: List[Dict]) -> str:
    """Extract text from content blocks."""
    text_parts = []
    for block in content_blocks:
        if isinstance(block, dict):
            if block.get('type') == 'text':
                text_parts.append(block.get('text', ''))
            elif block.get('type') == 'thinking':
                # Skip thinking blocks for main content
                pass
        elif isinstance(block, str):
            text_parts.append(block)
    return '\n'.join(text_parts).strip()


def extract_thinking_content(content_blocks: List[Dict]) -> Optional[str]:
    """Extract thinking content if present."""
    for block in content_blocks:
        if isinstance(block, dict) and block.get('type') == 'thinking':
            return block.get('thinking', '')
    return None


def extract_tool_calls(content_blocks: List[Dict]) -> List[Dict[str, Any]]:
    """Extract tool_use blocks from content."""
    tools = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get('type') == 'tool_use':
            tools.append({
                'id': block.get('id'),
                'name': block.get('name'),
                'input': block.get('input', {})
            })
    return tools


def extract_tool_results(content_blocks: List[Dict]) -> List[Dict[str, Any]]:
    """Extract tool_result blocks from content."""
    results = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get('type') == 'tool_result':
            output = block.get('content', '')
            # Truncate long outputs
            if isinstance(output, str) and len(output) > 5000:
                output = output[:2500] + '\n\n[... truncated ...]\n\n' + output[-2500:]
            results.append({
                'tool_use_id': block.get('tool_use_id'),
                'content': output,
                'is_error': block.get('is_error', False)
            })
    return results


def extract_session(jsonl_path: Path) -> SessionData:
    """
    Parse a Claude Code session JSONL file and extract structured data.

    Args:
        jsonl_path: Path to the .jsonl session file

    Returns:
        SessionData object with all extracted information
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Session file not found: {jsonl_path}")

    # Initialize session data
    session = SessionData(
        session_id=jsonl_path.stem,
        project_name="",
        project_path="",
        branch="main",
        start_time=datetime.now(),
        end_time=datetime.now(),
        duration_minutes=0
    )

    # Track file operations
    file_ops = {
        'read': set(),
        'modified': set(),
        'created': set(),
        'deleted': set()
    }

    # Track tool calls by ID for matching with results
    pending_tools = {}

    # Parse JSONL line by line
    lines = jsonl_path.read_text().splitlines()

    for line_num, line in enumerate(lines):
        if not line.strip():
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            session.errors.append(f"Line {line_num}: JSON parse error: {e}")
            continue

        obj_type = obj.get('type')

        # Extract session summary (usually first line)
        if obj_type == 'summary':
            session.summaries.append(obj.get('summary', ''))
            session.title = obj.get('summary', '')

        # Extract user messages
        elif obj_type == 'user':
            timestamp = datetime.fromisoformat(obj['timestamp'].replace('Z', '+00:00'))

            # Update session metadata
            if line_num == 1 or not session.project_path:  # First real message
                session.project_path = obj.get('cwd', '')
                session.branch = obj.get('gitBranch', 'main')
                session.start_time = timestamp
                # Derive project name from path
                if session.project_path:
                    session.project_name = Path(session.project_path).name

            session.end_time = timestamp

            # Extract message content
            message_content = obj.get('message', {})
            content_blocks = message_content.get('content', [])

            # Handle string content or list of blocks
            if isinstance(content_blocks, str):
                text = content_blocks
                tool_results = []
            else:
                text = extract_text_content(content_blocks)
                tool_results = extract_tool_results(content_blocks)

            # Match tool results with pending tool calls
            for result in tool_results:
                tool_id = result.get('tool_use_id')
                if tool_id in pending_tools:
                    pending_tools[tool_id].output = result.get('content', '')
                    if result.get('is_error'):
                        session.errors.append(f"Tool error: {result.get('content', '')[:200]}")

            # Create message
            if text or tool_results:  # Only add if there's actual content
                msg = Message(
                    uuid=obj.get('uuid', ''),
                    role='user',
                    content=text,
                    timestamp=timestamp,
                    tool_results=tool_results
                )
                session.messages.append(msg)

        # Extract assistant messages
        elif obj_type == 'assistant':
            timestamp = datetime.fromisoformat(obj['timestamp'].replace('Z', '+00:00'))
            session.end_time = timestamp

            message_content = obj.get('message', {})
            content_blocks = message_content.get('content', [])

            # Extract model info
            if not session.model:
                session.model = message_content.get('model', '')

            # Extract slug
            if not session.slug:
                session.slug = obj.get('slug', '')

            # Extract text and thinking
            text = extract_text_content(content_blocks)
            thinking = extract_thinking_content(content_blocks)
            tool_calls_data = extract_tool_calls(content_blocks)

            # Process tool calls
            for tool_data in tool_calls_data:
                tool = ToolCall(
                    name=tool_data['name'],
                    input=tool_data['input'],
                    timestamp=timestamp,
                    message_uuid=obj.get('uuid', '')
                )
                session.tool_calls.append(tool)
                pending_tools[tool_data['id']] = tool

                # Track file operations
                tool_input = tool_data['input']
                if tool_data['name'] == 'Read':
                    file_path = tool_input.get('file_path', '')
                    if file_path:
                        file_ops['read'].add(file_path)

                elif tool_data['name'] in ['Edit', 'Write']:
                    file_path = tool_input.get('file_path', '')
                    if file_path:
                        # Determine if it's a create or modify
                        # (We'll refine this with file-history-snapshot data)
                        file_ops['modified'].add(file_path)

                elif tool_data['name'] == 'Bash':
                    command = tool_input.get('command', '')
                    description = tool_input.get('description', '')

                    cmd = Command(
                        command=command,
                        description=description,
                        output="",  # Will be filled by tool_result
                        timestamp=timestamp,
                        message_uuid=obj.get('uuid', '')
                    )
                    session.commands.append(cmd)

            # Create message
            if text or thinking or tool_calls_data:
                msg = Message(
                    uuid=obj.get('uuid', ''),
                    role='assistant',
                    content=text,
                    timestamp=timestamp,
                    thinking=thinking,
                    tool_calls=tool_calls_data
                )
                session.messages.append(msg)

        # Extract file history
        elif obj_type == 'file-history-snapshot':
            snapshot = obj.get('snapshot', {})
            tracked_files = snapshot.get('trackedFileBackups', {})

            for file_path in tracked_files.keys():
                file_ops['modified'].add(file_path)

    # Calculate duration
    duration = (session.end_time - session.start_time).total_seconds() / 60
    session.duration_minutes = int(duration)

    # Consolidate file operations
    session.files_read = sorted(list(file_ops['read']))
    session.files_modified = sorted(list(file_ops['modified']))

    # Determine created vs modified (files in modified but not in read before first write)
    # This is a heuristic - files created in this session likely weren't read first
    for file_path in session.files_modified:
        # Simple heuristic: if it was modified but never read, it was likely created
        if file_path not in session.files_read:
            session.files_created.append(file_path)

    # Remove created files from modified list
    session.files_modified = [f for f in session.files_modified if f not in session.files_created]

    return session


def find_project_claude_dir(project_path: Path) -> Path:
    """
    Find the Claude storage directory for a given project.

    Args:
        project_path: Path to the project root

    Returns:
        Path to the Claude projects directory for this project
    """
    # Mangle the path like Claude does
    # Example: /Users/bilalmahmud/Repository/castclub
    # Becomes: -Users-bilalmahmud-Repository-castclub
    mangled = project_path.as_posix().replace('/', '-')
    claude_dir = Path.home() / '.claude' / 'projects' / mangled

    if not claude_dir.exists():
        raise FileNotFoundError(f"Claude project directory not found: {claude_dir}")

    return claude_dir


def find_git_root(start_path: Path) -> Path:
    """Find the git repository root from a starting path."""
    current = start_path.resolve()

    while current != current.parent:
        if (current / '.git').exists():
            return current
        current = current.parent

    raise FileNotFoundError(f"Not in a git repository: {start_path}")


def list_sessions(project_path: Optional[Path] = None) -> List[tuple]:
    """
    List all sessions for a project.

    Args:
        project_path: Path to project root (defaults to current directory)

    Returns:
        List of (session_id, size, modified_time) tuples, sorted by time
    """
    if project_path is None:
        project_path = find_git_root(Path.cwd())

    claude_dir = find_project_claude_dir(project_path)

    sessions = []
    for jsonl_file in claude_dir.glob('*.jsonl'):
        if jsonl_file.stat().st_size > 0:  # Skip empty files
            sessions.append((
                jsonl_file.stem,
                jsonl_file.stat().st_size,
                datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            ))

    # Sort by modification time (newest first)
    sessions.sort(key=lambda x: x[2], reverse=True)

    return sessions
