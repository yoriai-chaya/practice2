import json
import sys
from pathlib import Path
from typing import List


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_stderr_messages(records: List[dict]) -> List[str]:
    return [r.get("message", "") for r in records if r.get("stream") == "stderr"]


def main(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"Input file {input_file} does not exist.", file=sys.stderr)
        sys.exit(1)

    data = load_json(input_file)

    error_count = int(data.get("summary", {}).get("errorCount", 0))
    if error_count == 0:
        print("No errors found in the build log.")
        sys.exit(0)

    records = data.get("records", [])
    messages = extract_stderr_messages(records)

    concat = "".join(m + "\n" for m in messages)
    payload = {"message": concat}

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    print(f"Extracted error message written to {output_file}")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python tool_extract_stderr_messages.py <input_file> <output_file>"
        )
        sys.exit(1)
    else:
        main(sys.argv[1], sys.argv[2])
