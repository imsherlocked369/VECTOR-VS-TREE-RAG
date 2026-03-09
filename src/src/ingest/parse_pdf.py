import argparse
import json
from pathlib import Path
from docling.document_converter import DocumentConverter
from src.common.utils import clean_markdown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to PDF")
    parser.add_argument("--output", required=True, help="Path to parsed JSON")
    args = parser.parse_args()

    pdf_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    markdown = clean_markdown(result.document.export_to_markdown())

    payload = {
        "doc_id": pdf_path.stem,
        "source_path": str(pdf_path),
        "markdown": markdown,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved parsed document to {out_path}")


if __name__ == "__main__":
    main()
