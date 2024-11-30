from pathlib import Path
import json
from typing import Dict, List, Any
from typing import Optional
from prompt_analyzer import create_handler
import time

RELEVANT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".kts",
    ".scala",
    ".pl",
    ".pm",
    ".r",
    ".sh",
    ".bat",
    ".ps1",
    ".lua",
    ".sql",
    ".html",
    ".css",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".ipynb",
    ".m",
    ".mm",
    ".vb",
    ".cs",
    ".fs",
    ".fsx",
    ".erl",
    ".hrl",
    ".ex",
    ".exs",
    ".dart",
    ".groovy",
    ".jl",
    ".clj",
    ".cljs",
    ".coffee",
    ".litcoffee",
    ".rkt",
    ".hs",
    ".lhs",
    ".ml",
    ".mli",
    ".nim",
    ".cr",
    ".nimble",
    ".hx",
    ".hxsl",
    ".hxproj",
    ".hxcpp",
    ".hxcs",
    ".hxjava",
    ".hxcpp",
    ".hxnode",
    ".hxphp",
    ".hxpy",
    ".hxrb",
    ".hxswf",
    ".hxvm",
    ".hxweb",
    ".hxwin",
    ".hxwpf",
    ".sol",
    ".vy",
}

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React",
    ".tsx": "React TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".rb": "Ruby",
    ".php": "PHP",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".scala": "Scala",
    ".pl": "Perl",
    ".pm": "Perl Module",
    ".r": "R",
    ".sh": "Shell",
    ".bat": "Batch",
    ".ps1": "PowerShell",
    ".lua": "Lua",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".xml": "XML",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".ipynb": "Jupyter Notebook",
    ".m": "MATLAB/Objective-C",
    ".mm": "Objective-C++",
    ".vb": "Visual Basic",
    ".cs": "C#",
    ".fs": "F#",
    ".fsx": "F# Script",
    ".erl": "Erlang",
    ".hrl": "Erlang Header",
    ".ex": "Elixir",
    ".exs": "Elixir Script",
    ".dart": "Dart",
    ".groovy": "Groovy",
    ".jl": "Julia",
    ".clj": "Clojure",
    ".cljs": "ClojureScript",
    ".coffee": "CoffeeScript",
    ".litcoffee": "Literate CoffeeScript",
    ".rkt": "Racket",
    ".hs": "Haskell",
    ".lhs": "Literate Haskell",
    ".ml": "OCaml",
    ".mli": "OCaml Interface",
    ".nim": "Nim",
    ".cr": "Crystal",
    ".nimble": "Nimble",
    ".hx": "Haxe",
    ".hxsl": "Haxe Shader",
    ".hxproj": "Haxe Project",
    ".hxcpp": "Haxe C++",
    ".hxcs": "Haxe C#",
    ".hxjava": "Haxe Java",
    ".hxnode": "Haxe Node.js",
    ".hxphp": "Haxe PHP",
    ".hxpy": "Haxe Python",
    ".hxrb": "Haxe Ruby",
    ".hxswf": "Haxe SWF",
    ".hxvm": "Haxe VM",
    ".hxweb": "Haxe Web",
    ".hxwin": "Haxe Windows",
    ".hxwpf": "Haxe WPF",
    ".sol": "Solidity",
    ".vy": "Vyper",
}

PACKAGE_FILES = {
    "package.json": "npm",
    "requirements.txt": "pip",
    "setup.py": "python",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "Gemfile": "bundler",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "go.sum": "go",
    "composer.json": "composer",
    "pubspec.yaml": "dart",
    "Project.toml": "julia",
    "mix.exs": "elixir",
    "Makefile": "make",
    "CMakeLists.txt": "cmake",
    "SConstruct": "scons",
    "build.xml": "ant",
    "Rakefile": "rake",
    "shard.yml": "crystal",
    "nim.cfg": "nim",
    "default.nix": "nix",
    "stack.yaml": "haskell",
    "rebar.config": "erlang",
    "rebar.lock": "erlang",
    "rebar3.config": "erlang",
    "rebar3.lock": "erlang",
    "project.clj": "leiningen",
    "deps.edn": "clojure",
    "build.boot": "boot",
    "build.sbt": "sbt",
    "Brewfile": "homebrew",
    "Vagrantfile": "vagrant",
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    "Procfile": "heroku",
    "tox.ini": "tox",
    "pyproject.toml": "poetry",
    "Pipfile": "pipenv",
    "Pipfile.lock": "pipenv",
    "environment.yml": "conda",
    "meta.yaml": "conda",
}


def analyze_repository_structure(repo_names: List[str], user_path: Path) -> Dict[str, Any]:
    """Processes source code from repositories to build LLM-friendly structure"""
    result = {}

    for repo_name in repo_names:
        username = user_path.name
        repo_path = (
            user_path / f"{username}_{repo_name}.git"
        )
        
        print("processing,", repo_name, "path:", repo_path)
        
        if not repo_path.exists():
            print("skipping")
            continue

        # Get the structure first
        structure = _build_tree_structure(repo_path)

        # Count language occurrences from the structure
        language_counts = {}
        for file_info in _get_source_files(structure):
            extension = file_info["extension"].lower()
            if extension in LANGUAGE_EXTENSIONS:
                language = LANGUAGE_EXTENSIONS[extension]
                language_counts[language] = language_counts.get(language, 0) + 1

        # Sort languages by frequency, most common first
        languages = sorted(
            language_counts.items(),
            key=lambda x: (-x[1], x[0])  # Sort by count descending, then name ascending
        )

        # Create the language string
        languages_str = ", ".join(lang for lang, _ in languages)

        result[repo_name] = {
            "structure": structure,
            "file_stats": _analyze_file_statistics(repo_path),
            "documentation": _extract_documentation(repo_path),
            "languages": languages_str
        }

    _extract_code_samples(result, user_path)

    return result


def _build_tree_structure(repo_path: Path, files_per_dir: int = 20, max_depth: int = 3) -> Dict[str, Any]:
    """
    Builds a tree representation of repository structure with limits.
    
    Args:
        repo_path: Repository path
        files_per_dir: Maximum number of files to include per directory (default: 20)
        max_depth: Maximum depth for nested directories (default: 3)
    """
    def create_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        tree = {
            "type": "directory",
            "name": path.name,
            "path": str(path.relative_to(repo_path)),
            "children": [],
        }

        # Stop traversing if we hit max depth
        if current_depth >= max_depth:
            tree["children"] = [{
                "type": "note",
                "message": f"Directory depth limit ({max_depth}) reached"
            }]
            return tree

        try:
            items = list(path.iterdir())
            
            # Skip git directory and common build artifacts
            if path.name in {
                ".git",
                "node_modules",
                "__pycache__",
                "build",
                "dist",
            }:
                return tree

            # Process files with limit
            files = [
                item for item in items 
                if item.is_file() and item.suffix.lower() in RELEVANT_EXTENSIONS
            ]
            if files:
                files = files[:files_per_dir]  # Limit number of files
                for item in files:
                    tree["children"].append({
                        "type": "file",
                        "name": item.name,
                        "path": str(item.relative_to(repo_path)),
                        "extension": item.suffix.lower(),
                        "size": item.stat().st_size,
                    })

            # Process directories
            dirs = [item for item in items if item.is_dir()]
            for item in dirs:
                subtree = create_tree(item, current_depth + 1)
                if subtree["children"]:  # Only add non-empty directories
                    tree["children"].append(subtree)
                        
        except PermissionError:
            pass

        return tree

    return create_tree(repo_path)


def _analyze_file_statistics(repo_path: Path) -> Dict[str, Any]:
    """Analyzes file statistics for the repository"""

    file_count = 0
    total_loc = 0

    for ext in LANGUAGE_EXTENSIONS:
        for file_path in repo_path.rglob(f"*{ext}"):
            if not any(p in str(file_path) for p in RELEVANT_EXTENSIONS):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    loc = len([l for l in content.splitlines() if l.strip()])
                    total_loc += loc
                    file_count += 1
            except (UnicodeDecodeError, PermissionError):
                continue

    return {
        "file_count": file_count,
        "total_loc": total_loc,
    }


def _extract_documentation(repo_path: Path) -> Dict[str, Any]:
    """Extracts documentation and metadata from repository"""
    docs = {}

    # Look for README
    readme_paths = list(repo_path.glob("README*"))
    if readme_paths:
        try:
            with open(readme_paths[0], "r", encoding="utf-8") as f:
                docs["readme"] = f.read()
        except (UnicodeDecodeError, PermissionError):
            docs["readme"] = None

    docs["package_info"] = {}
    for filename, pkg_type in PACKAGE_FILES.items():
        pkg_path = repo_path / filename
        if pkg_path.exists():
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    docs["package_info"][pkg_type] = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue

    return docs


def _extract_code_samples(sources_data: Dict[str, Any], user_path: Path, max_file_size: int = 100000) -> Dict[str, Any]:
    """
    Extracts code samples for files identified as relevant by Gemini.
    Filters out files larger than max_file_size bytes.
    """
    handler = create_handler()

    try:
        # Preprocess to remove large files from consideration
        filtered_structures = {}
        for repo_name, repo_data in sources_data.items():
            structure_copy = repo_data["structure"].copy()
            
            # Filter function to remove large files
            def filter_large_files(node):
                if node.get("type") == "directory":
                    node["children"] = [
                        child for child in node.get("children", [])
                        if child.get("type") == "directory" 
                        or (child.get("type") == "file" and child.get("size", 0) <= max_file_size)
                    ]
                    for child in node["children"]:
                        if child.get("type") == "directory":
                            filter_large_files(child)
                return node
            
            # Apply filter
            filtered_structures[repo_name] = filter_large_files(structure_copy)

        # Create a combined prompt for all repositories
        prompt = f"""
            Analyze the repository structures and identify the most relevant files for codebase analysis.
            
            Focus on files that would reveal:
            1. Core functionality and architecture
            2. Main business logic
            3. Key utilities and helpers
            4. Configuration and setup

            Results will be used for further code analysis. Remember to include ALL relevant files, especially for fullstack applications. Be thorough but concise. Avoid including non-original code, e.g., dependencies or libraries code. AVOID INCLUDING MORE THAN 50 FILES PER REPOSITORY!!! TRY TO INCLUDE LESS THAN 20 IF POSSIBLE. CORE_FILES ARE THE PRIORITY, YOU CAN OMITT THE REST IF IT EXCEEDS THE LIMIT.

            Return a JSON object with these categories:
            
            {{
                "repositories": {{ // MANDATORY highest level key
                    "repo_name": {{ // MANDATORY name of the repository you are analyzing
                        "core_files": ["list of most important files"], // MAX 20 files!
                        "secondary_files": ["list of supporting files"], // MAX 20 files!
                        "config_files": ["list of relevant config files"] // MAX 10 files!
                    }},
                    "repo_name": {{...}},
                }}
            }}
            
            CRITICAL REQUIREMENTS:
            
            Limit each list of most important files to a maximum of 20 files!!!
            
            Avoid including binary files or large data files. Only include files that are essential for understanding the codebase. Avoid including too many files, focus on the most important ones. Avoid including files that user did not write, e.g., dependencies or libraries code. Avoid including utility files that are not essential for understanding the codebase. Focus on including only source code, some repositories may have a lot of files, but only a few are essential for understanding the codebase. Do not include long .json files or other artifact type of files - notice "size" of the file in the structure.

            Repository structures:
            {json.dumps(filtered_structures, indent=2)}
            
            Only include files that exist in the structure. Return valid JSON format.
            DO NOT wrap the JSON in markdown code blocks. 
        """

        # Get file categories for all repositories
        file_categories = handler.generate_json_response(prompt)

        if not file_categories:
            print("Skipping due to API error")
            return sources_data

        for repo_name, repo_data in sources_data.items():
            repo_data["samples"] = {
                "core_files": {},
                "utility_files": {},
                "config_files": {}
            }

            # Filter out large files from consideration
            all_files = {
                file_info["path"]: file_info 
                for file_info in _get_source_files(repo_data["structure"])
                if file_info.get("size", 0) <= max_file_size
            }

            for category in ["core_files", "utility_files", "config_files"]:
                for file_path in file_categories["repositories"].get(repo_name, {}).get(category, []):
                    if file_path not in all_files:
                        continue

                    source_code = _read_source_file(user_path, repo_name, file_path)
                    if source_code:
                        repo_data["samples"][category][file_path] = source_code

    except Exception as e:
        print(f"Error processing code samples: {str(e)}")

    return sources_data


def _get_source_files(structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Helper to recursively extract source files from tree structure"""
    files = []

    def traverse(node: Dict[str, Any]):
        if not isinstance(node, dict):
            return

        # If it's a file, add it
        if node.get("type") == "file":
            files.append(node)

        # If it's a directory, traverse its children
        elif node.get("type") == "directory" and "children" in node:
            for child in node.get("children", []):
                traverse(child)

        # Also check any other dictionaries that might contain nested structures
        for value in node.values():
            if isinstance(value, dict):
                traverse(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        traverse(item)

    traverse(structure)

    # Sort files by path for consistent ordering
    return sorted(files, key=lambda x: x["path"])


def _read_source_file(user_path: Path, repo_name: str, file_path: str) -> Optional[str]:
    """Reads source code from file with proper error handling"""
    try:
        # Construct the full path to the source file
        full_path = user_path / f"{user_path.name}_{repo_name}.git" / file_path

        # Check if file exists and is readable
        if not full_path.is_file():
            return None

        # Common binary file extensions to skip
        if full_path.suffix.lower() not in RELEVANT_EXTENSIONS:
            return None

        # Try to read the file with different encodings
        encodings = ["utf-8", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(full_path, "r", encoding=encoding) as f:
                    content = f.read()

                    # Basic validation of text content
                    if "\0" in content:  # Binary file check
                        return None

                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error reading {full_path}: {str(e)}")
                return None

        return None

    except Exception as e:
        print(f"Error accessing {file_path}: {str(e)}")
        return None