from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re

"""
BHYT XML Data Models – 12 Bảng
Nguồn tiêu chí: Quyết định 130/QĐ-BYT, đính chính theo Quyết định 4750/QĐ-BYT
Tự động sinh từ file Excel tiêu chí.
 
Mỗi class:
  - Định nghĩa tên trường (field name) khớp với XML / Excel
  - Ghi rõ kiểu dữ liệu (str / float / int / Optional)
  - Ghi rõ max_length (None = không giới hạn)
  - Phương thức validate() trả về list[str] chứa các lỗi
"""
# ---------------------------------------------------------------------------
# Base class – chứa logic validate chung
# ---------------------------------------------------------------------------
 
class BHYTBase:
    """Base class cho tất cả bảng BHYT. Subclass chỉ cần khai báo field.""" 
    # Mỗi subclass override 2 dict này
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {}
    _NUMERIC: ClassVar[set] = set()          # tên field kiểu Số
    _DATE12: ClassVar[set] = set()           # yyyymmddHHMM (12 ký tự)
    _DATE8: ClassVar[set] = set()            # yyyymmdd (8 ký tự)
 
    def validate(self) -> list[str]:
        errors = []
        for f in fields(self):  # type: ignore[arg-type]
            name = f.name
            val = getattr(self, name)
            val_str = "" if val is None else str(val).strip()
 
            # --- Kiểm tra kích thước tối đa ---
            max_len = self._MAX_LEN.get(name)
            if max_len and val_str and len(val_str) > max_len:
                errors.append(
                    f"[{name}] Quá kích thước: {len(val_str)} > {max_len} ký tự "
                    f"(giá trị: {val_str[:40]}...)"
                )
 
            # --- Kiểm tra kiểu Số ---
            if name in self._NUMERIC and val_str:
                try:
                    float(val_str.replace(",", ""))
                except ValueError:
                    errors.append(
                        f"[{name}] Sai kiểu dữ liệu – cần Số, nhận: '{val_str}'"
                    )
 
            # --- Kiểm tra định dạng ngày 12 ký tự (yyyymmddHHMM) ---
            if name in self._DATE12 and val_str:
                if not re.fullmatch(r"\d{12}", val_str):
                    errors.append(
                        f"[{name}] Sai định dạng – cần yyyymmddHHMM (12 số), nhận: '{val_str}'"
                    )
 
            # --- Kiểm tra định dạng ngày 8 ký tự (yyyymmdd) ---
            if name in self._DATE8 and val_str:
                for part in val_str.split(";"):
                    part = part.strip()
                    if part and not re.fullmatch(r"\d{8}", part):
                        errors.append(
                            f"[{name}] Sai định dạng – cần yyyymmdd (8 số), nhận: '{part}'"
                        )
 
        return errors
 
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BHYTBase":
        """Tạo instance từ dict (row từ pandas / Excel)."""
        init_args = {}
        field_names = {f.name for f in fields(cls)}  # type: ignore[arg-type]
        for f in fields(cls):  # type: ignore[arg-type]
            raw = d.get(f.name, None)
            if raw is None or (isinstance(raw, float) and str(raw) == "nan"):
                init_args[f.name] = None
            else:
                init_args[f.name] = str(raw).strip() if str(raw).strip() != "nan" else None
        return cls(**init_args)