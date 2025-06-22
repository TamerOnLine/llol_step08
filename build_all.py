import os
import re
import subprocess
import sys

README_PATH = "README.md"
OUTPUT_PATH = "docs/index.md"
LICENSE_LINK = "https://github.com/PostgresCraft/encryption_service/blob/main/LICENSE"

def read_readme(path=README_PATH):
    """
    Read the content of the README file.

    Args:
        path (str): Path to the README file.

    Returns:
        str: The content of the README file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def clean_content(content: str) -> str:
    """
    Clean the README content by removing live documentation and back-to-top links.

    Args:
        content (str): Raw content from the README file.

    Returns:
        str: Cleaned content.
    """
    content = re.sub(r".*?\[Live Documentation\]\([^)]+\)\s*\n?", "", content)
    content = re.sub(r"\[.*?Back to Top.*?\]\([^)]+\)\s*\n?", "", content, flags=re.IGNORECASE)
    content = re.sub(r"## Table of Contents[\s\S]+?(?=\n## )", "", content)
    return content

def fix_links(content: str) -> str:
    """
    Replace local LICENSE links with full GitHub link and fix image paths.

    Args:
        content (str): Cleaned README content.

    Returns:
        str: Content with fixed links.
    """
    content = content.replace("screenshots/", "screenshots/")
    content = content.replace("(../LICENSE)", f"({LICENSE_LINK})")
    content = content.replace("(LICENSE)", f"({LICENSE_LINK})")
    return content

def write_to_docs(content: str, output_path=OUTPUT_PATH):
    """
    Write the processed content to the documentation path.

    Args:
        content (str): Final processed content.
        output_path (str): Path to write the documentation.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

import subprocess
import sys

def run_script(description: str, command: list) -> bool:
    """
    Execute a shell command with logging (for CLI).

    Args:
        description (str): Description of the command being run.
        command (list): Command to execute as list of strings.

    Returns:
        bool: True if command executed successfully, False otherwise.
    """
    print(f"\n🔧 {description}...\n")
    try:
        subprocess.run(command, check=True)
        print(f"✅ Success: {description} completed.\n")
        return True
    except subprocess.CalledProcessError as error:
        print(f"❌ Error during {description}: {error}\n")
        return False

    
def check_virtual_environment():
    if sys.prefix == sys.base_prefix:
        import platform
        if platform.system() == "Windows":
            activate_cmd = ".\\venv\\Scripts\\Activate"
        else:
            activate_cmd = "source venv/bin/activate"

        print("❌ You are not inside a virtual environment (venv).")
        print(f"👉 Please activate it first using:\n   {activate_cmd}\n")
        sys.exit(1)


def main():
    """
    Main function to process README and build documentation.
    """
    check_virtual_environment()  # ← تحقق من تفعيل venv أولًا

    print("Starting full build process...\n")

    # Step 0: Setup folder structure
    run_script("Setting up documentation structure", [sys.executable, "setup_docs_structure.py"])

    # Step 1: Prepare documentation files
    if not run_script("Executing prepare_docs.py", [sys.executable, "prepare_docs.py"]):
        return

    # Step 2: Build site using MkDocs
    if not run_script("Running mkdocs build", ["mkdocs", "build"]):
        return

    print("\nAll steps completed successfully.")

if __name__ == "__main__":
    main()