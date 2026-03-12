"""CLI for Resume & JD Matcher."""

import json
import sys
from pathlib import Path

import typer

from app.services import matcher, parser

app = typer.Typer(help="Resume & JD Matcher CLI")


def _read_input(path_or_stdin: str) -> str:
    """Read content from file path or stdin if path is '-'."""
    if path_or_stdin == "-":
        return sys.stdin.read()
    p = Path(path_or_stdin)
    if not p.exists():
        typer.echo(f"Error: file not found: {p}", err=True)
        raise typer.Exit(1)
    return p.read_text(encoding="utf-8", errors="replace")


@app.callback(invoke_without_command=True)
def main(
    resume: str = typer.Option(..., "--resume", "-r", help="Path to resume file (PDF or .txt) or '-' for stdin"),
    jd: str = typer.Option(..., "--jd", "-j", help="Path to job description file or '-' for stdin"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
) -> None:
    """Score resume against job description."""
    # Load job description
    jd_text = _read_input(jd).strip()
    if not jd_text:
        typer.echo("Error: job description is empty.", err=True)
        raise typer.Exit(1)

    # Load resume: from file (PDF or text) or stdin
    if resume == "-":
        resume_text = sys.stdin.read().strip()
        if not resume_text:
            typer.echo("Error: resume content from stdin is empty.", err=True)
            raise typer.Exit(1)
    else:
        p = Path(resume)
        if not p.exists():
            typer.echo(f"Error: file not found: {p}", err=True)
            raise typer.Exit(1)
        try:
            resume_text = parser.parse_resume(file_path=p)
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    try:
        result = matcher.match_resume_to_jd(resume_text, jd_text)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if json_output:
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"Score: {result['score']} / 100")
        typer.echo(f"Explanation: {result['explanation']}")


if __name__ == "__main__":
    app()
