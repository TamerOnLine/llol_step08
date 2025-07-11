import os
import re
import subprocess
from pathlib import Path
from flask import request
from deep_translator import GoogleTranslator
from .extensions import babel

# ----------- Path Settings -----------
STEP_DIR = Path(__file__).resolve().parent
BABEL_CFG = os.path.join(STEP_DIR, "babel.cfg")
OUTPUT_DIR = STEP_DIR / "translations"
POT_FILE = STEP_DIR / "messages.pot"
LANGUAGES = ["ar", "de"]
# -------------------------------------

def fix_placeholders(msgid, translated):
    """
    Ensure placeholders in translations match the original format.

    Args:
        msgid (str): Original message ID.
        translated (str): Translated message.

    Returns:
        str: Corrected translation with proper placeholders.
    """
    patterns = [
        re.compile(r"%\([^)]+\)s"),    # e.g., %(name)s
        re.compile(r"\{[^}]+\}")       # e.g., {value}
    ]
    for pattern in patterns:
        placeholders = pattern.findall(msgid)
        for ph in placeholders:
            corrupted_regex = re.compile(rf"%\s*\(\s*{re.escape(ph[2:-2])}\s*\)\s*s", re.IGNORECASE)
            translated = corrupted_regex.sub('', translated)
            if ph not in translated:
                print(f"Missing placeholder {ph} in translation → fixing.")
                translated = translated.strip()
                if not translated.endswith(ph):
                    translated += f" {ph}"
    return translated

def read_pot_file(path):
    """Read a .pot file and return its lines."""
    return path.read_text(encoding="utf-8").splitlines()

def init_translators(langs):
    """Initialize translators for specified languages."""
    return {lang: GoogleTranslator(source='en', target=lang) for lang in langs}

def add_po_header(lines, lang):
    """Add standard PO file header."""
    header = [
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        f'"Language: {lang}\\n"',
        ""
    ]
    return header + lines

def is_english(text):
    """Check if the text contains English characters only."""
    return re.search(r'[a-zA-Z]', text) and not re.search(r'[ء-ي]', text)

def translate_lines(lines, translators):
    """
    Translate lines using provided translators.

    Args:
        lines (list): Lines from the .pot file.
        translators (dict): Dictionary of language codes and translators.

    Returns:
        dict: Translated content for each language.
    """
    msgid = None
    translated_content = {lang: [] for lang in translators}

    for line in lines:
        if 'fuzzy' in line:
            continue
        if line.startswith('msgid '):
            msgid_raw = line[6:].strip().strip('"')
            if not is_english(msgid_raw):
                msgid = None
                for lang in translators:
                    translated_content[lang].append(line)
                    translated_content[lang].append('msgstr ""')
                continue
            msgid = msgid_raw
            for lang in translators:
                translated_content[lang].append(line)
        elif line.strip() == 'msgstr ""' and msgid:
            for lang, translator in translators.items():
                try:
                    translated = translator.translate(msgid)
                    if not translated.strip():
                        print(f"Warning [{lang}] Empty translation for: {msgid}")
                    translated = fix_placeholders(msgid, translated)
                    translated_content[lang].append(f'msgstr "{translated}"')
                    print(f"Translated [{lang}] {msgid} → {translated}")
                except Exception as e:
                    translated_content[lang].append('msgstr ""')
                    print(f"Error [{lang}] translating '{msgid}': {e}")
            msgid = None
        else:
            for lang in translators:
                translated_content[lang].append(line)
    return translated_content

def save_translations(translated_content, base_output_dir):
    """
    Save translated content into .po files for each language.

    Args:
        translated_content (dict): Translated lines by language.
        base_output_dir (Path): Base output directory.
    """
    for lang, lines in translated_content.items():
        lines = add_po_header(lines, lang)
        path = Path(base_output_dir) / lang / "LC_MESSAGES" / "messages.po"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Saved [{lang}] to {path}")

def generate_pot_file():
    """Extract translation phrases into a .pot file."""
    print("Extracting phrases to .pot file ...")
    subprocess.run(["pybabel", "extract", "-F", BABEL_CFG, "-o", POT_FILE, STEP_DIR], check=True)

def init_po_files(languages):
    """Initialize .po files for specified languages."""
    for lang in languages:
        po_path = Path(OUTPUT_DIR) / lang / "LC_MESSAGES" / "messages.po"
        if not po_path.exists():
            print(f"Initializing file for [{lang}] ...")
            subprocess.run(["pybabel", "init", "-i", POT_FILE, "-d", OUTPUT_DIR, "-l", lang], check=True)
        else:
            print(f"Translation file already exists for [{lang}]")

def compile_translations():
    """Compile .po files into .mo files."""
    try:
        subprocess.run(["pybabel", "compile", "-d", OUTPUT_DIR], check=True)
        print("Compiled translations to .mo files.")
    except subprocess.CalledProcessError as e:
        print("Error compiling .mo files:", e)

def main():
    """Main execution logic for translation generation."""
    generate_pot_file()
    init_po_files(LANGUAGES)

    if not Path(POT_FILE).exists():
        print(f"{POT_FILE} not found after extraction.")
        return

    lines = read_pot_file(Path(POT_FILE))
    translators = init_translators(LANGUAGES)
    translated_content = translate_lines(lines, translators)
    save_translations(translated_content, OUTPUT_DIR)
    compile_translations()

    if Path(POT_FILE).exists():
        Path(POT_FILE).unlink()
        print("Temporary messages.pot file deleted.")

if __name__ == "__main__":
    main()