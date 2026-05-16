"""
TAI Profile Layered Generator v0.1
Purpose: Split a tagged profile md file into four levels (L0-L3),
         and generate hashes and authorization tokens.
Usage: python tai_split.py
"""

import hashlib
import json
import secrets
import re
from datetime import datetime, date
from pathlib import Path


# ── Configuration (edit here) ──────────────────────────────────
INPUT_FILE = "AI_digital_human_profile_XXX_tagged.md"   # Tagged source file
OUTPUT_DIR = "tai_output"                                # Output directory
PROFILE_ID = "TAI-XXX-001"                              # Unique profile ID
OWNER_NAME = "XXX"                                       # Profile owner
# ────────────────────────────────────────────────────────────────


LEVEL_NAMES = {
    "L0": "Public Layer",
    "L1": "Authorized Layer",
    "L2": "Restricted Layer",
    "L3": "Local Only Layer",
}

LEVEL_DESCRIPTIONS = {
    "L0": "Transmittable over any network; used for basic AI personalization",
    "L1": "Requires authorization; core data for deep AI personalization",
    "L2": "Local encrypted storage only; contains sensitive cognitive features",
    "L3": "Never leaves local device; raw data and contact information",
}


def parse_tagged_file(filepath: str) -> dict[str, list[str]]:
    """
    Parse an md file with <!-- TAI:Lx --> ... <!-- TAI:END --> tags.
    Returns: {"L0": [block1, block2, ...], "L1": [...], ...}
    """
    content = Path(filepath).read_text(encoding="utf-8")
    blocks = {"L0": [], "L1": [], "L2": [], "L3": []}

    # Extract YAML front matter (untagged; goes into L0)
    yaml_match = re.match(r"^(---\n.*?\n---\n)", content, re.DOTALL)
    if yaml_match:
        blocks["L0"].append(yaml_match.group(1))

    # Extract all tagged blocks
    pattern = r"<!-- TAI:(L[0-3]) -->(.*?)<!-- TAI:END -->"
    matches = re.findall(pattern, content, re.DOTALL)

    for level, block_content in matches:
        if level in blocks:
            blocks[level].append(block_content.strip())

    # Extract untagged H2 headers as the skeleton structure,
    # so every level file has the complete section headers as a scaffold.
    section_headers = re.findall(r"^## .+$", content, re.MULTILINE)

    return blocks, section_headers


def build_level_content(blocks: dict, section_headers: list, target_level: str) -> str:
    """
    Build the full content for the specified level.
    Rule: L1 includes L0+L1, L2 includes L0+L1+L2, L3 includes everything.
    """
    level_order = ["L0", "L1", "L2", "L3"]
    target_idx = level_order.index(target_level)
    included_levels = level_order[: target_idx + 1]

    header = f"""---
tai_profile_id: {PROFILE_ID}
tai_level: {target_level}
tai_level_name: {LEVEL_NAMES[target_level]}
tai_description: {LEVEL_DESCRIPTIONS[target_level]}
generated_at: {datetime.now().isoformat()}
owner: {OWNER_NAME}
---

"""
    if target_level == "L3":
        warning = (
            "⚠️  L3 layer: Never leaves local device. Contains raw data, "
            "contact information, mentor relationships, and other highly "
            "sensitive information.\n\n"
        )
        header += warning
    elif target_level == "L2":
        warning = (
            "⚠️  L2 layer: Local encrypted storage only. Contains salary "
            "expectations, financial goals, decision red lines, and other "
            "sensitive information.\n\n"
        )
        header += warning

    content_parts = [header]

    for level in included_levels:
        if blocks.get(level):
            if level != "L0":  # L0 shown directly; other levels get a small annotation
                content_parts.append(f"\n<!-- Content below is from the {level} layer -->\n")
            for block in blocks[level]:
                content_parts.append(block + "\n")

    return "\n".join(content_parts)


def sha256_file(content: str) -> str:
    """Compute the SHA-256 hash of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def generate_token(level: str, profile_id: str) -> str:
    """Generate an authorization token in the format TAI-{LEVEL}-{16-byte hex}."""
    random_part = secrets.token_hex(16)
    return f"TAI-{level}-{random_part}"


def create_token_file(
    level: str,
    profile_hash: str,
    token: str,
    granted_to: str = "unspecified",
    valid_days: int = 90,
) -> dict:
    """Build the JSON structure for an authorization token."""
    today = date.today()
    expiry = date(today.year, today.month, today.day)

    # Compute expiry date
    from datetime import timedelta
    expiry = today + timedelta(days=valid_days)

    return {
        "tai_token_version": "0.1",
        "profile_id": PROFILE_ID,
        "profile_owner": OWNER_NAME,
        "access_level": level,
        "level_name": LEVEL_NAMES[level],
        "granted_to": granted_to,
        "issued_at": today.isoformat(),
        "valid_until": expiry.isoformat(),
        "profile_hash": profile_hash,
        "token": token,
        "verification_note": (
            f"Verification method for the recipient: compute SHA-256 over the "
            f"contents of the received {level}_profile.md file. The result should "
            f"exactly match the profile_hash field in this file."
        ),
    }


def main():
    print("=" * 55)
    print("  TAI Profile Layered Generator v0.1")
    print("=" * 55)

    # Check input file
    if not Path(INPUT_FILE).exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    print(f"✅ Output directory: {output_path.resolve()}\n")

    # Parse the tagged file
    print("📖 Parsing tagged file...")
    blocks, section_headers = parse_tagged_file(INPUT_FILE)

    for level, content_list in blocks.items():
        print(f"   {level}: found {len(content_list)} content blocks")

    print()

    # Generate files for each level
    manifest = {
        "tai_manifest_version": "0.1",
        "profile_id": PROFILE_ID,
        "owner": OWNER_NAME,
        "generated_at": datetime.now().isoformat(),
        "levels": {}
    }

    level_contents = {}

    for level in ["L0", "L1", "L2", "L3"]:
        print(f"🔨 Generating {level} layer...")

        # Build content
        content = build_level_content(blocks, section_headers, level)
        level_contents[level] = content

        # Write md file
        md_filename = f"{level}_profile_{PROFILE_ID}.md"
        md_path = output_path / md_filename
        md_path.write_text(content, encoding="utf-8")
        print(f"   📄 File: {md_filename}")

        # Compute hash
        file_hash = sha256_file(content)
        print(f"   🔑 SHA-256: {file_hash[:16]}...{file_hash[-8:]}")

        # Generate token (none for L3, which never transmits)
        if level != "L3":
            token = generate_token(level, PROFILE_ID)
            token_data = create_token_file(
                level=level,
                profile_hash=file_hash,
                token=token,
                granted_to="TBD (please specify the authorized recipient before use)",
                valid_days=90,
            )
            token_filename = f"{level}_token_{PROFILE_ID}.json"
            token_path = output_path / token_filename
            token_path.write_text(
                json.dumps(token_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"   🎫 Token: {token_filename}")

            manifest["levels"][level] = {
                "file": md_filename,
                "hash": file_hash,
                "token_file": token_filename,
                "token_prefix": token[:20] + "...",
            }
        else:
            manifest["levels"][level] = {
                "file": md_filename,
                "hash": file_hash,
                "token_file": "None (L3 never transmits; no token generated)",
                "note": "This file should only exist locally; do not transmit or grant access to any third party.",
            }

        print()

    # Write the manifest summary file
    manifest_path = output_path / f"manifest_{PROFILE_ID}.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("=" * 55)
    print("✅ Done!")
    print(f"   Output directory: {output_path.resolve()}")
    print(f"   Manifest file: manifest_{PROFILE_ID}.json")
    print()
    print("📋 Usage notes:")
    print("   L0 layer: can be sent directly to any AI platform")
    print("   L1 layer: when sharing with an authorized partner, include L1_token_*.json")
    print("   L2 layer: local use only; transmission not recommended")
    print("   L3 layer: never transmit; no token")
    print()
    print("⚠️  Remember to update the granted_to field in the token file before authorizing!")
    print("=" * 55)


if __name__ == "__main__":
    main()
