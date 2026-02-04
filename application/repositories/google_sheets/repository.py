from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
import difflib

from application.repositories.google_sheets.columns import C


class SheetsSchemaError(RuntimeError):
    pass


# --- колонки, в которые сервис ИМЕЕТ ПРАВО писать ---
# supplier + purchase_price = только ручной ввод -> НЕ ПИШЕМ
WRITABLE_COLUMNS = {
    # business
    C.name,
    C.qty,
    C.order_number,
    C.commission,
    C.buyer_price,
    C.payout,
    C.ship_date,
    C.status,

    # service
    C.key,
    C.row_type,
    C.ship_date_iso,
}

ROW_TYPE_HEADER = "DAY_HEADER"
ROW_TYPE_ITEM = "ITEM"
ROW_TYPE_SUMMARY = "DAY_SUMMARY"


def _norm(s: str) -> str:
    s = (s or "")
    s = str(s).strip().lower().replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" %", "%")
    return s


@dataclass
class SheetsRepository:
    service: Any
    spreadsheet_id: str
    sheet_name: str

    # кэш: чтобы не дергать заголовок 100 раз
    _col_map_cache: Optional[Dict[str, int]] = field(default=None, init=False, repr=False)
    _sheet_id_cache: Optional[int] = field(default=None, init=False, repr=False)

    # -------------------------
    # A1 helpers
    # -------------------------
    def _col_to_a1(self, col_idx_0: int) -> str:
        n = col_idx_0 + 1
        s = ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    def _sheet_ref(self) -> str:
        """
        Корректная ссылка на лист для A1-нотации.
        Всегда оборачиваем в одинарные кавычки, чтобы не думать о пробелах/символах.
        """
        safe = (self.sheet_name or "").replace("'", "''")
        return f"'{safe}'"

    # -------------------------
    # Schema / columns
    # -------------------------
    def _get_header_row(self) -> List[str]:
        # Важно: A1-range должен содержать буквы колонок
        resp = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self._sheet_ref()}!A1:ZZ1",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        values = resp.get("values", [])
        return values[0] if values else []

    def build_column_map(self, force_refresh: bool = False) -> Dict[str, int]:
        """
        Возвращает маппинг: каноническое имя (из C) -> индекс (0-based).
        Требуем, чтобы ВСЕ нужные колонки существовали в таблице.
        """
        if self._col_map_cache is not None and not force_refresh:
            return self._col_map_cache

        header = self._get_header_row()
        if not header:
            raise SheetsSchemaError("Header row is empty.")

        norm_to_idx: Dict[str, int] = {}
        for idx, h in enumerate(header):
            if not h:
                continue
            norm_to_idx.setdefault(_norm(h), idx)

        required = [
            # ручные
            C.supplier,
            C.purchase_price,

            # автоматические
            C.name,
            C.qty,
            C.order_number,
            C.commission,
            C.buyer_price,
            C.payout,
            C.ship_date,
            C.status,

            # служебные
            C.key,
            C.row_type,
            C.ship_date_iso,
        ]

        col_map: Dict[str, int] = {}
        missing: List[str] = []

        for col in required:
            idx = norm_to_idx.get(_norm(col))
            if idx is None:
                missing.append(col)
            else:
                col_map[col] = idx

        if missing:
            all_norm = list(norm_to_idx.keys())
            lines = []
            for m in missing:
                close = difflib.get_close_matches(_norm(m), all_norm, n=3, cutoff=0.55)
                close_raw = [f"'{header[norm_to_idx[c]]}'" for c in close]
                hint = f" closest: {', '.join(close_raw)}" if close_raw else ""
                lines.append(f"- {m}{hint}")
            raise SheetsSchemaError("Missing required columns:\n" + "\n".join(lines))

        self._col_map_cache = col_map
        return col_map

    # -------------------------
    # SheetId / insert rows
    # -------------------------
    def _get_sheet_id(self, force_refresh: bool = False) -> int:
        """
        sheetId ищем по properties.title (это РЕАЛЬНОЕ имя вкладки, БЕЗ кавычек).
        """
        if self._sheet_id_cache is not None and not force_refresh:
            return self._sheet_id_cache

        meta = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        for sh in meta.get("sheets", []):
            props = sh.get("properties", {})
            if props.get("title") == self.sheet_name:
                self._sheet_id_cache = int(props["sheetId"])
                return self._sheet_id_cache

        raise SheetsSchemaError(f"Sheet '{self.sheet_name}' not found (check GOOGLE_SHEET_NAME)")

    def insert_empty_rows(self, start_row_index_1based: int, count: int) -> dict:
        sheet_id = self._get_sheet_id()
        start0 = start_row_index_1based - 1
        body = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start0,
                            "endIndex": start0 + count,
                        },
                        "inheritFromBefore": True,
                    }
                }
            ]
        }
        return self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body
        ).execute()

    # -------------------------
    # PATCH update (точечно)
    # -------------------------
    def patch_row_cells(self, col_map: Dict[str, int], row_idx_1: int, values: Dict[str, Any]) -> dict:
        data = []
        for col_name, v in values.items():
            if col_name not in WRITABLE_COLUMNS:
                continue
            if col_name not in col_map:
                continue
            if v is None:
                continue

            col_a1 = self._col_to_a1(col_map[col_name])
            rng = f"{self._sheet_ref()}!{col_a1}{row_idx_1}:{col_a1}{row_idx_1}"
            data.append({"range": rng, "values": [[v]]})

        if not data:
            return {"updated": 0, "reason": "no writable values"}

        body = {"valueInputOption": "USER_ENTERED", "data": data}
        return self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body
        ).execute()

    # -------------------------
    # Read service columns (stable)
    # -------------------------
    def _batch_get_columns(self, col_letters: List[str]) -> Dict[str, List[str]]:
        ranges = [f"{self._sheet_ref()}!{c}2:{c}" for c in col_letters]
        resp = self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.spreadsheet_id,
            ranges=ranges,
            valueRenderOption="FORMATTED_VALUE",
        ).execute()

        out: Dict[str, List[str]] = {c: [] for c in col_letters}
        for vr in resp.get("valueRanges", []):
            r = vr.get("range", "")
            m = re.search(r"!(?P<col>[A-Z]+)\d+:", r)
            if not m:
                continue
            letter = m.group("col")

            col_vals = vr.get("values", [])
            out[letter] = [row[0] if row else "" for row in col_vals]

        max_len = max((len(v) for v in out.values()), default=0)
        for k in out:
            if len(out[k]) < max_len:
                out[k].extend([""] * (max_len - len(out[k])))
        return out

    def _get_first_empty_row_1(self, col_map: Dict[str, int]) -> int:
        key_col = self._col_to_a1(col_map[C.key])
        cols = self._batch_get_columns([key_col])
        return len(cols[key_col]) + 2

    # -------------------------
    # Find helpers (by service cols)
    # -------------------------
    def find_item_row_by_key(self, col_map: Dict[str, int], key: str) -> Optional[int]:
        key_col = self._col_to_a1(col_map[C.key])
        cols = self._batch_get_columns([key_col])
        keys = cols[key_col]

        target = str(key).strip()
        for i in range(len(keys)):
            if str(keys[i]).strip() == target:
                return i + 2
        return None

    def find_day_header_row(self, col_map: Dict[str, int], ship_date_iso: str) -> Optional[int]:
        ship_col = self._col_to_a1(col_map[C.ship_date_iso])
        type_col = self._col_to_a1(col_map[C.row_type])

        cols = self._batch_get_columns([ship_col, type_col])
        ships = cols[ship_col]
        types = cols[type_col]

        for i in range(len(ships)):
            if str(types[i]).strip() == ROW_TYPE_HEADER and str(ships[i]).strip() == str(ship_date_iso).strip():
                return i + 2
        return None

    def find_day_summary_row(self, col_map: Dict[str, int], ship_date_iso: str) -> Optional[int]:
        ship_col = self._col_to_a1(col_map[C.ship_date_iso])
        type_col = self._col_to_a1(col_map[C.row_type])

        cols = self._batch_get_columns([ship_col, type_col])
        ships = cols[ship_col]
        types = cols[type_col]

        for i in range(len(ships)):
            if str(types[i]).strip() == ROW_TYPE_SUMMARY and str(ships[i]).strip() == str(ship_date_iso).strip():
                return i + 2
        return None

    def find_first_day_row(self, col_map: Dict[str, int], ship_date_iso: str) -> Optional[int]:
        ship_col = self._col_to_a1(col_map[C.ship_date_iso])
        cols = self._batch_get_columns([ship_col])
        ships = cols[ship_col]

        target = str(ship_date_iso).strip()
        for i in range(len(ships)):
            if str(ships[i]).strip() == target:
                return i + 2
        return None

    # -------------------------
    # Day block (create/repair)
    # -------------------------
    def ensure_day_block(self, col_map: Dict[str, int], ship_date_iso: str) -> dict:
        header_row = self.find_day_header_row(col_map, ship_date_iso)
        summary_row = self.find_day_summary_row(col_map, ship_date_iso)

        if header_row is not None and summary_row is not None:
            return {"created": False, "repaired": False, "header_row": header_row, "summary_row": summary_row}

        if header_row is None and summary_row is not None:
            first_day_row = self.find_first_day_row(col_map, ship_date_iso)
            insert_at = first_day_row if first_day_row is not None else summary_row

            self.insert_empty_rows(insert_at, 1)
            new_header = insert_at

            self.patch_row_cells(col_map, new_header, {
                C.row_type: ROW_TYPE_HEADER,
                C.ship_date_iso: ship_date_iso,
                C.ship_date: ship_date_iso,
                C.key: f"day:{ship_date_iso}:header",
                C.name: f"Дата отгрузки: {ship_date_iso}",
            })

            new_summary = summary_row + 1 if insert_at <= summary_row else summary_row
            return {"created": True, "repaired": True, "header_row": new_header, "summary_row": new_summary}

        if header_row is not None and summary_row is None:
            ship_col = self._col_to_a1(col_map[C.ship_date_iso])
            type_col = self._col_to_a1(col_map[C.row_type])
            cols = self._batch_get_columns([ship_col, type_col])
            ships = cols[ship_col]

            target = str(ship_date_iso).strip()

            last_day_row = None
            for i in range(len(ships)):
                if str(ships[i]).strip() == target:
                    last_day_row = i + 2

            insert_at = (last_day_row + 1) if last_day_row is not None else (header_row + 1)

            self.insert_empty_rows(insert_at, 1)
            new_summary = insert_at

            self.patch_row_cells(col_map, new_summary, {
                C.row_type: ROW_TYPE_SUMMARY,
                C.ship_date_iso: ship_date_iso,
                C.key: f"day:{ship_date_iso}:summary",
                C.name: "ИТОГО ЗА ДЕНЬ",
            })

            return {"created": True, "repaired": True, "header_row": header_row, "summary_row": new_summary}

        first_empty = self._get_first_empty_row_1(col_map)
        self.insert_empty_rows(first_empty, 2)

        header_row_1 = first_empty
        summary_row_1 = first_empty + 1

        self.patch_row_cells(col_map, header_row_1, {
            C.row_type: ROW_TYPE_HEADER,
            C.ship_date_iso: ship_date_iso,
            C.ship_date: ship_date_iso,
            C.key: f"day:{ship_date_iso}:header",
            C.name: f"Дата отгрузки: {ship_date_iso}",
        })

        self.patch_row_cells(col_map, summary_row_1, {
            C.row_type: ROW_TYPE_SUMMARY,
            C.ship_date_iso: ship_date_iso,
            C.key: f"day:{ship_date_iso}:summary",
            C.name: "ИТОГО ЗА ДЕНЬ",
        })

        return {"created": True, "repaired": False, "header_row": header_row_1, "summary_row": summary_row_1}

    # -------------------------
    # Upsert ITEM
    # -------------------------
    def upsert_item(self, values: Dict[str, Any]) -> dict:
        """
        values должны содержать:
        - C.ship_date_iso (YYYY-MM-DD)
        - C.key
        """
        col_map = self.build_column_map()
        ship_date_iso = str(values[C.ship_date_iso]).strip()

        info = self.ensure_day_block(col_map, ship_date_iso)
        summary_row = info["summary_row"]

        existing_row = self.find_item_row_by_key(col_map, values[C.key])
        if existing_row is not None:
            return self.patch_row_cells(col_map, existing_row, values)

        self.insert_empty_rows(summary_row, 1)
        new_row = summary_row
        return self.patch_row_cells(col_map, new_row, values)
