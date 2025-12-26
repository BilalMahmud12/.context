#!/usr/bin/env python3
"""
Session Distiller for AgentShell

Extracts and summarizes Claude Code sessions into git-trackable markdown.

Usage:
    distill.py [session-id]           # Distill specific session
    distill.py --latest                # Distill most recent session
    distill.py --list                  # List recent sessions
    distill.py --no-ai [session-id]    # Skip AI summarization

Examples:
    distill.py 359ddc91-b696-476e-8ad8-5c707647800a
    distill.py --latest
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    from jinja2 import Template, Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 package not installed")
    print("Install with: pip install jinja2")
    sys.exit(1)

from extractors import (
    extract_session,
    find_git_root,
    find_project_claude_dir,
    list_sessions
)
from summarizers import summarize_session


def find_session_file(identifier: str) -> Path:
    """
    Find a session JSONL file by ID or path.

    Args:
        identifier: Session UUID, slug, or full path to JSONL file

    Returns:
        Path to the session file

    Raises:
        FileNotFoundError: If session cannot be found
    """
    # Check if it's a full path
    path = Path(identifier)
    if path.exists() and path.suffix == '.jsonl':
        return path

    # Try to find in current project's Claude directory
    try:
        project_root = find_git_root(Path.cwd())
        claude_dir = find_project_claude_dir(project_root)

        # Try as session ID
        session_file = claude_dir / f"{identifier}.jsonl"
        if session_file.exists():
            return session_file

        # Try finding by slug or partial match
        for jsonl_file in claude_dir.glob('*.jsonl'):
            if identifier in jsonl_file.stem:
                return jsonl_file

    except FileNotFoundError:
        pass

    raise FileNotFoundError(f"Session not found: {identifier}")


def get_latest_session() -> Path:
    """
    Get the most recent session file for the current project.

    Returns:
        Path to the latest session file

    Raises:
        FileNotFoundError: If no sessions found
    """
    try:
        project_root = find_git_root(Path.cwd())
        sessions = list_sessions(project_root)

        if not sessions:
            raise FileNotFoundError("No sessions found for this project")

        # Return most recent (sessions are sorted newest first)
        session_id, _, _ = sessions[0]
        claude_dir = find_project_claude_dir(project_root)
        return claude_dir / f"{session_id}.jsonl"

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Cannot find sessions: {e}")


def list_recent_sessions():
    """
    List recent sessions for the current project.
    """
    try:
        project_root = find_git_root(Path.cwd())
        print(f"\nRecent sessions for {project_root.name}:\n")

        sessions = list_sessions(project_root)

        if not sessions:
            print("No sessions found.")
            return

        print(f"{'Session ID':<40} {'Size':>10} {'Modified'}")
        print("-" * 80)

        for session_id, size, modified in sessions[:20]:  # Show last 20
            size_kb = size / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            modified_str = modified.strftime("%Y-%m-%d %H:%M")

            print(f"{session_id:<40} {size_str:>10} {modified_str}")

        print(f"\nShowing {min(20, len(sessions))} of {len(sessions)} sessions")
        print(f"\nTo distill a session: distill.py <session-id>")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


def generate_filename(session) -> str:
    """
    Generate a filename for the session summary.

    Args:
        session: SummarizedSession object

    Returns:
        Filename (without extension)
    """
    # Use date and derive topic from title
    date = session.date
    title = session.title.lower()

    # Extract meaningful words from title
    # Remove common words and keep significant ones
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = [w for w in title.split() if w.isalnum() and w not in stop_words]

    # Take first 3-4 meaningful words
    topic_words = words[:4]
    topic = '-'.join(topic_words) if topic_words else 'session'

    # Clean up topic (remove special chars)
    topic = ''.join(c if c.isalnum() or c == '-' else '-' for c in topic)
    topic = '-'.join(filter(None, topic.split('-')))  # Remove empty parts

    # Limit length
    if len(topic) > 50:
        topic = topic[:47] + '...'

    return f"{date}-{topic}"


def render_template(session) -> str:
    """
    Render the session summary using the Jinja2 template.

    Args:
        session: SummarizedSession object

    Returns:
        Rendered markdown content
    """
    script_dir = Path(__file__).parent
    template_dir = script_dir / 'templates'

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('session-summary.md.j2')

    # Convert dataclass to dict for template
    context = {
        'title': session.title,
        'date': session.date,
        'duration': session.duration,
        'session_id': session.session_id,
        'branch': session.branch,
        'agent': session.agent,
        'model': session.model,
        'summary_paragraph': session.summary_paragraph,
        'user_requests': session.user_requests,
        'starting_state': session.starting_state,
        'narrative': session.narrative,
        'key_decisions': session.key_decisions,
        'blockers': session.blockers,
        'code_snippets': session.code_snippets,
        'search_keywords': session.search_keywords,
        'files_created': session.files_created,
        'files_modified': session.files_modified,
        'files_deleted': session.files_deleted,
        'commands': session.commands,
        'related_tasks': session.related_tasks,
        'raw_session_path': session.raw_session_path
    }

    return template.render(**context)


def main():
    """Main entry point for the distiller."""
    parser = argparse.ArgumentParser(
        description='Distill Claude Code sessions into markdown summaries'
    )
    parser.add_argument(
        'session',
        nargs='?',
        help='Session ID or path to JSONL file'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Distill the most recent session'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List recent sessions'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI summarization (faster, less detailed)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory (default: docs/sessions/)'
    )

    args = parser.parse_args()

    # Handle --list
    if args.list:
        list_recent_sessions()
        return

    # Determine which session to process
    if args.latest:
        print("Finding latest session...")
        try:
            session_path = get_latest_session()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.session:
        print(f"Finding session: {args.session}")
        try:
            session_path = find_session_file(args.session)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    print(f"✓ Found session: {session_path.name}")

    # Extract session data
    print("\nExtracting session data...")
    try:
        session_data = extract_session(session_path)
    except Exception as e:
        print(f"Error extracting session: {e}")
        sys.exit(1)

    print(f"✓ Extracted {len(session_data.messages)} messages, {len(session_data.tool_calls)} tool calls")

    # Summarize
    use_ai = not args.no_ai
    if use_ai:
        print("\nSummarizing with AI...")
    else:
        print("\nGenerating summary (AI disabled)...")

    try:
        summarized = summarize_session(session_data, use_ai=use_ai)
    except Exception as e:
        print(f"Error summarizing session: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"✓ Generated summary")

    # Render template
    print("\nRendering markdown...")
    try:
        markdown = render_template(summarized)
    except Exception as e:
        print(f"Error rendering template: {e}")
        sys.exit(1)

    print(f"✓ Rendered template ({len(markdown)} characters)")

    # Determine output path
    if args.output:
        output_dir = Path(args.output)
    else:
        try:
            project_root = find_git_root(Path.cwd())
            output_dir = project_root / 'docs' / 'sessions'
        except FileNotFoundError:
            output_dir = Path.cwd() / 'docs' / 'sessions'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = generate_filename(summarized)
    output_path = output_dir / f"{filename}.draft.md"

    # Write output
    output_path.write_text(markdown)

    print(f"\n✓ Draft saved to: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Review: code {output_path}")
    print(f"  2. Edit as needed")
    print(f"  3. Finalize: mv {output_path} {output_dir}/{filename}.md")
    print(f"  4. Commit: git add docs/sessions/ && git commit -m 'docs: Session summary'")


if __name__ == '__main__':
    main()
