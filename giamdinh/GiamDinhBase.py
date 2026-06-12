from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GiamDinhError:
    """Một lỗi giám định thanh toán BHYT."""
    sheet: str          # Sheet XML chứa dịch vụ bị từ chối
    ma_lk: str          # Mã lần khám
    row_excel: int      # Dòng Excel (tính từ 2)
    ma_ly_do: str       # Mã lý do từ chối: S011.1, S054.1, D004.1, S059.2, S079.1...
    mo_ta: str          # Mô tả chi tiết lý do
    can_cu: str         # Căn cứ pháp lý (tên QĐ/TT)
    ma_dich_vu: str = ""   # Mã DVKT hoặc mã thuốc bị từ chối (nếu có)


class GiamDinhBase(ABC):
    """
    Base class cho tất cả rule giám định.
    Mỗi văn bản/nhóm quy định → 1 class con.
    """

    @abstractmethod
    def check(self, all_objects: dict) -> list[GiamDinhError]:
        """
        Nhận toàn bộ all_objects (dict sheet_name → list[BHYTBase]),
        trả về danh sách GiamDinhError.
        """
        ...

    # ------------------------------------------------------------------
    # Helper dùng chung
    # ------------------------------------------------------------------
    @staticmethod
    def _get_rows(all_objects: dict, sheet: str):
        """Trả về list (row_excel, record) của một sheet."""
        return list(enumerate(all_objects.get(sheet, []), start=2))

    @staticmethod
    def _group_by_ma_lk(rows):
        """Group list[(row_excel, record)] theo MA_LK."""
        result: dict[str, list] = {}
        for row_excel, record in rows:
            key = getattr(record, "MA_LK", None) or ""
            result.setdefault(key, []).append((row_excel, record))
        return result