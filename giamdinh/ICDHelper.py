"""
ICDHelper – Tiện ích xử lý và so khớp mã ICD-10 dùng chung cho toàn bộ layer giám định.

Cấu trúc dữ liệu ICD trong XML1:
  MA_BENH_CHINH : str  – 1 mã duy nhất        VD: "E11.9"
  MA_BENH_KT    : str  – nhiều mã, phân cách ";"  VD: "E78.2;I10;K58.9;Z76.0"

Dùng:
    from giamdinh.ICDHelper import ICDHelper

    icd = ICDHelper.from_record(rec)          # rec là object XML1
    icd.has_any({"N18", "N17"})               # True/False
    icd.has_all({"E11", "I10"})               # True/False
    icd.main_matches({"E10", "E11"})          # chỉ kiểm MA_BENH_CHINH
    icd.codes                                 # frozenset tất cả mã đã parse
"""

from __future__ import annotations


class ICDHelper:
    """
    Wrapper cho cặp (MA_BENH_CHINH, MA_BENH_KT) của một lần khám.

    So khớp hỗ trợ prefix:
      - "N18.5" match ref "N18"   (mã cụ thể ⊂ nhóm cha)   → code.startswith(ref)
      - "N18"   match ref "N18.5" CHỈ KHI code đủ dài ≥ 3   → tránh "I1" match "I10"

    Tất cả so sánh đều KHÔNG phân biệt hoa/thường sau khi chuẩn hóa.
    """

    __slots__ = ("_main", "_kt", "_all")

    # ------------------------------------------------------------------
    # Khởi tạo
    # ------------------------------------------------------------------
    def __init__(self, ma_benh_chinh: str | None, ma_benh_kt: str | None):
        self._main: frozenset[str] = self._parse(ma_benh_chinh)
        self._kt:   frozenset[str] = self._parse(ma_benh_kt)
        self._all:  frozenset[str] = self._main | self._kt

    @classmethod
    def from_record(cls, record) -> "ICDHelper":
        """Tạo từ object dataclass XML1 (hoặc bất kỳ object có 2 attribute tương ứng)."""
        chinh = getattr(record, "MA_BENH_CHINH", None) or ""
        kt    = getattr(record, "MA_BENH_KT",    None) or ""
        return cls(chinh, kt)

    @classmethod
    def from_dict(cls, d: dict) -> "ICDHelper":
        """Tạo từ dict {"MA_BENH_CHINH": ..., "MA_BENH_KT": ...}."""
        return cls(d.get("MA_BENH_CHINH", ""), d.get("MA_BENH_KT", ""))

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def main(self) -> frozenset[str]:
        """Tập mã chính (MA_BENH_CHINH) – thường chỉ 1 phần tử."""
        return self._main

    @property
    def kt(self) -> frozenset[str]:
        """Tập mã kèm theo (MA_BENH_KT) – nhiều phần tử."""
        return self._kt

    @property
    def codes(self) -> frozenset[str]:
        """Tất cả mã (chính + kèm)."""
        return self._all

    # ------------------------------------------------------------------
    # API so khớp chính
    # ------------------------------------------------------------------
    def has_any(self, ref_set: set[str] | frozenset[str]) -> bool:
        """
        True nếu bất kỳ mã nào (chính hoặc kèm) khớp với ít nhất 1 ref.
        So khớp prefix hai chiều có kiểm soát độ dài.
        """
        return any(self._match_one(code, ref_set) for code in self._all)

    def has_all(self, ref_set: set[str] | frozenset[str]) -> bool:
        """
        True nếu MỖI ref trong ref_set đều có ít nhất 1 mã bệnh khớp.
        Dùng khi cần BN phải có đồng thời nhiều bệnh.
        """
        return all(
            any(self._match_one(code, {ref}) for code in self._all)
            for ref in ref_set
        )

    def main_matches(self, ref_set: set[str] | frozenset[str]) -> bool:
        """
        True nếu MA_BENH_CHINH khớp với ít nhất 1 ref.
        Dùng khi quy định chỉ áp dụng theo chẩn đoán chính.
        """
        return any(self._match_one(code, ref_set) for code in self._main)

    def kt_matches(self, ref_set: set[str] | frozenset[str]) -> bool:
        """
        True nếu MA_BENH_KT có ít nhất 1 mã khớp với ref_set.
        Dùng khi muốn kiểm tra riêng bệnh kèm.
        """
        return any(self._match_one(code, ref_set) for code in self._kt)

    def none_of(self, ref_set: set[str] | frozenset[str]) -> bool:
        """True nếu KHÔNG có mã nào khớp — dùng kiểm tra điều kiện được hưởng."""
        return not self.has_any(ref_set)

    # ------------------------------------------------------------------
    # Helper nội bộ
    # ------------------------------------------------------------------
    @staticmethod
    def _parse(value: str | None) -> frozenset[str]:
        """
        Parse chuỗi ICD (single hoặc multi-value phân cách ";") thành frozenset.
        Chuẩn hóa: strip, upper.
        """
        if not value:
            return frozenset()
        return frozenset(
            c.strip().upper()
            for c in str(value).split(";")
            if c.strip()
        )

    @staticmethod
    def _match_one(code: str, ref_set: set[str] | frozenset[str]) -> bool:
        """
        So khớp 1 mã với tập ref.

        Luật:
          1. Bằng nhau chính xác               : "I10"   == "I10"   → True
          2. code cụ thể hơn ref (prefix match) : "N18.5".startswith("N18") → True
          3. ref cụ thể hơn code               : chỉ cho phép khi len(code) >= 3
                                                  tránh "I1".startswith → "I10" nhầm
        """
        code_u = code.upper()
        for ref in ref_set:
            ref_u = ref.upper()
            if code_u == ref_u:
                return True
            if code_u.startswith(ref_u):        # N18.5 khớp nhóm N18
                return True
            if len(code_u) >= 3 and ref_u.startswith(code_u):  # N18 khớp N18.5
                return True
        return False

    # ------------------------------------------------------------------
    # Tiện ích debug
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        main_str = ", ".join(sorted(self._main)) or "(trống)"
        kt_str   = ", ".join(sorted(self._kt))   or "(trống)"
        return f"ICDHelper(main={main_str} | kt={kt_str})"