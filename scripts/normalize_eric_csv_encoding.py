from pathlib import Path


FILES = [
    (
        Path("data/raw/nhs_eric/eric_2023_24_site_data.csv"),
        Path("data/raw/nhs_eric/eric_2023_24_site_data_utf8.csv"),
    ),
    (
        Path("data/raw/nhs_eric/eric_2024_25_site_data.csv"),
        Path("data/raw/nhs_eric/eric_2024_25_site_data_utf8.csv"),
    ),
]


def normalize_file(source: Path, target: Path) -> None:
    raw_bytes = source.read_bytes()

    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = raw_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError("unknown", b"", 0, 1, f"Unable to decode {source}")

    target.write_text(text, encoding="utf-8", newline="")


def main() -> None:
    for source, target in FILES:
        normalize_file(source, target)
        print(f"normalized {source} -> {target}")


if __name__ == "__main__":
    main()
