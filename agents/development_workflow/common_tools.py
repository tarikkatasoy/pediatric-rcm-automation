import pathlib
import subprocess

# --- Path Safety Configuration ---
# Resolves the root directory of the Pediatric RCM project.
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.resolve()


def safe_path(file_path: str) -> pathlib.Path:
    """Resolves an agent-provided path against the REPO_ROOT for security."""
    resolved_path = (REPO_ROOT / file_path).resolve()
    # Ensure the path remains within the project boundaries (Security Gatekeeper)
    if REPO_ROOT != resolved_path and REPO_ROOT not in resolved_path.parents:
        raise ValueError("Error: Access denied. Path is outside project boundaries.")
    return resolved_path


def read_file(path: str) -> str:
    """Reads clinical notes, knowledge base files, or encounter drafts."""
    try:
        return safe_path(path).read_text()
    except Exception as e:
        return f"Error reading file {path}: {e}"


def onboard_project() -> str:
    """Reads the README.md to provide the agent with Pediatric Associates clinic context."""
    readme_path = "README.md"
    try:
        return read_file(path=readme_path)
    except Exception as e:
        return f"Error: Could not read {readme_path}. {e}"


def write_file(path: str, content: str) -> str:
    """Saves billing drafts or finalized encounter reports to the system."""
    try:
        safe_path(path).write_text(content)
        return f"File {path} successfully saved."
    except Exception as e:
        return f"Error writing file {path}: {e}"


def search_knowledge_base(query: str, file_path: str = "knowledge_base/billing_codes.md") -> str:
    """
    Searches the billing manual for specific keywords (e.g., 'Asthma', 'Scenario 4').
    This is preferred over reading the whole file to save tokens and increase precision.
    """
    try:
        content = read_file(file_path)
        lines = content.splitlines()
        # Find lines that contain the query (case-insensitive)
        matches = [line for line in lines if query.lower() in line.lower()]
        
        if not matches:
            return f"No matches found for '{query}' in {file_path}."
        
        return "\n".join(matches)
    except Exception as e:
        return f"Error searching knowledge base: {e}"


def list_directory(path: str) -> list[str]:
    """Lists available clinical notes or resource folders."""
    try:
        root = safe_path(path)
        files = [str(p.relative_to(REPO_ROOT)) for p in root.glob('**/*')]
        return files
    except Exception as e:
        return [f"Error listing directory {path}: {e}"]


# --- INTERNAL UTILITY TOOLS (Not for Medical Agent Use) ---

def run_shell_command(command: str) -> str:
    """
    Internal utility to run system commands. 
    WARNING: Do not expose this tool to LLM Agents to maintain security compliance.
    """
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            shell=True,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Command failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"


def list_git_files() -> str:
    """Lists files tracked by Git (excludes .venv and other ignored files)."""
    return run_shell_command(command="git ls-files")