import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class ImportedEntry:
    title: str
    website: str
    username: str
    password: str
    notes: str = ""
    category: str = "Imported"
    favorite: bool = False


class ImportService:
    SUPPORTED_SOURCES = ("Chrome", "Edge", "Firefox", "Bitwarden", "KeePass", "CSV")

    def import_csv(self, vault_service, csv_path: str, source: str) -> int:
        if source not in self.SUPPORTED_SOURCES:
            raise ValueError("Unsupported import source.")
        with open(csv_path, newline="", encoding="utf-8-sig") as file_handle:
            rows = list(csv.DictReader(file_handle))
        imported = [self._map_row(row, source) for row in rows]
        valid_entries = [entry for entry in imported if entry.website and entry.username and entry.password]
        for entry in valid_entries:
            vault_service.save_entry(
                title=entry.title or entry.website,
                website=entry.website,
                username=entry.username,
                password=entry.password,
                notes=entry.notes,
                category=entry.category,
                favorite=entry.favorite,
            )
        return len(valid_entries)

    def _map_row(self, row: dict[str, str], source: str) -> ImportedEntry:
        values = {str(key).strip().lower(): (value or "").strip() for key, value in row.items()}
        if source == "Bitwarden":
            return ImportedEntry(
                title=values.get("name", ""),
                website=values.get("login_uri", ""),
                username=values.get("login_username", ""),
                password=values.get("login_password", ""),
                notes=values.get("notes", ""),
                category=values.get("folder", "") or "Imported",
                favorite=values.get("favorite", "").lower() in {"1", "true"},
            )
        return ImportedEntry(
            title=values.get("name", "") or values.get("title", ""),
            website=values.get("url", "") or values.get("website", ""),
            username=values.get("username", "") or values.get("login_username", ""),
            password=values.get("password", "") or values.get("login_password", ""),
            notes=values.get("note", "") or values.get("notes", ""),
            category="Imported",
        )
