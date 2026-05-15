# ===========================================================================
# PATCH: Thêm __post_init__ vào BHYTBase để clean Excel text-prefix "'"
# Áp dụng cho toàn bộ XML1–XML14, không cần sửa từng class con.
#
# Nguyên nhân: Excel cell format Text → openpyxl đọc ra chuỗi có "'" ở đầu
# Ví dụ: "'202401011030" thay vì "202401011030"
# ===========================================================================

from dataclasses import dataclass, fields
from typing import Optional, ClassVar, Dict
from datetime import datetime
from services.helper import parse_date12, parse_date8, to_int, to_float, decimal_places


@dataclass
class BHYTBase:
    """Base class cho tất cả bảng XML BHYT."""

    # --- ClassVar khai báo ở các class con ---
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {}
    _NUMERIC: ClassVar[set] = set()
    _DATE12:  ClassVar[set] = set()
    _DATE8:   ClassVar[set] = set()

    # -----------------------------------------------------------------------
    # __post_init__: tự động clean toàn bộ field string sau khi khởi tạo
    # Chạy 1 lần duy nhất, trước bất kỳ validation nào.
    # -----------------------------------------------------------------------
    def __post_init__(self):
        for f in fields(self):
            raw = getattr(self, f.name)
            setattr(self, f.name, self._clean_excel_str(raw))

    # -----------------------------------------------------------------------
    # from_dict: khởi tạo object từ dict pandas (row_dict)
    # Chỉ lấy các key khớp với field của class, bỏ qua cột thừa trong Excel.
    # -----------------------------------------------------------------------
    @classmethod
    def from_dict(cls, row_dict: dict):
        """
        Tạo instance từ dict đọc bởi pandas.
        - Lọc chỉ lấy key trùng tên field của dataclass
        - Bỏ qua cột Excel thừa không có trong class
        - Giá trị rỗng ("", NaN) → None (để __post_init__ clean tiếp)
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered = {}
        for key, val in row_dict.items():
            if key not in valid_fields:
                continue
            # pandas fillna("") → chuỗi rỗng, hoặc "nan" → coi là None
            if val is None or str(val).strip() in ("", "nan", "NaN", "None"):
                filtered[key] = None
            else:
                filtered[key] = val
        return cls(**filtered)


    # -----------------------------------------------------------------------
    # _clean_excel_str: strip Excel quote-prefix và whitespace thừa
    # -----------------------------------------------------------------------
    @staticmethod
    def _clean_excel_str(value):
        """
        Xử lý giá trị đọc từ Excel:
          - Bỏ khoảng trắng đầu/cuối
          - Bỏ ký tự "'" ở đầu (Excel text-prefix do format cell = Text)
          - Trả None nếu chuỗi rỗng sau khi clean
          - Giữ nguyên nếu không phải str (int, float, None)
        """
        if not isinstance(value, str):
            return value
        v = value.strip()
        if v.startswith("'"):
            v = v[1:].strip()
        return v if v else None

    # -----------------------------------------------------------------------
    # validate: base chỉ kiểm _MAX_LEN, _NUMERIC, _DATE12, _DATE8
    # Class con override để thêm logic nghiệp vụ
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Shared parse helpers – wrapper từ services.helper
    # Expose làm @staticmethod để class con dùng qua self._xxx() hoặc cls._xxx()
    # -----------------------------------------------------------------------
    @staticmethod
    def _parse_date12(value) -> Optional[datetime]:
        return parse_date12(value)

    @staticmethod
    def _parse_date8(value) -> Optional[datetime]:
        return parse_date8(value)

    @staticmethod
    def _to_float(value) -> Optional[float]:
        return to_float(value)

    @staticmethod
    def _to_int(value) -> Optional[int]:
        return to_int(value)

    @staticmethod
    def _decimal_places(value) -> int:
        return decimal_places(value)

    def validate(self) -> list[str]:
        errs: list[str] = []

        for fname, max_len in self._MAX_LEN.items():
            val = getattr(self, fname, None)
            if val and max_len and len(str(val)) > max_len:
                errs.append(
                    f"{fname}: độ dài {len(str(val))} vượt quá {max_len} ký tự"
                )

        for fname in self._NUMERIC:
            val = getattr(self, fname, None)
            if val is not None:
                try:
                    float(str(val))
                except (ValueError, TypeError):
                    errs.append(f"{fname}: '{val}' không phải số hợp lệ")

        for fname in self._DATE12:
            val = getattr(self, fname, None)
            if val:
                s = str(val)
                if len(s) != 12 or not s.isdigit():
                    errs.append(
                        f"{fname}: '{val}' sai định dạng DATE12, "
                        "phải là yyyymmddHHMM (12 chữ số)"
                    )

        for fname in self._DATE8:
            val = getattr(self, fname, None)
            if val:
                s = str(val)
                if len(s) != 8 or not s.isdigit():
                    errs.append(
                        f"{fname}: '{val}' sai định dạng DATE8, "
                        "phải là yyyymmdd (8 chữ số)"
                    )

        return errs