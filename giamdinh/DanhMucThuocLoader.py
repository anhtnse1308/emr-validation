"""
DanhMucThuocLoader – Đọc và đánh chỉ mục file danh mục thuốc trúng thầu.

Cấu trúc file danh mục (FileDanhMucThuoc.xlsx):
  MA_THUOC    – mã hoạt chất/nhóm thuốc (vd: 40.685)
  SO_DANG_KY  – số đăng ký lưu hành (vd: VD-27543-17)
  TEN_THUOC   – tên thương mại
  TEN_HOAT_CHAT
  DON_VI_TINH
  HAM_LUONG
  DUONG_DUNG / MA_DUONG_DUNG
  DANG_BAO_CHE
  DON_GIA / DON_GIA_BH
  SO_LUONG    – số lượng trúng thầu
  TT_THAU     – số quyết định thầu
  TU_NGAY     – hiệu lực từ (DATE8)
  DEN_NGAY    – hiệu lực đến (DATE8, null = còn hiệu lực)
  MA_CSKCB    – mã cơ sở KCB áp dụng
  LOAI_THUOC  – 1=thuốc hóa dược, 2=YHCT
  LOAI_THAU   – 1=gói thầu tập trung, 2=gói thầu địa phương

Dùng:
    loader = DanhMucThuocLoader("path/to/FileDanhMucThuoc.xlsx")
    entry  = loader.lookup(ma_thuoc="40.685", so_dang_ky="VD-27543-17")
    # → DrugEntry | None
    entries = loader.lookup_all(ma_thuoc="40.685")
    # → list[DrugEntry]
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from collections import defaultdict


@dataclass
class DrugEntry:
    """1 dòng trong danh mục thuốc trúng thầu."""
    ma_thuoc:     str
    so_dang_ky:   str
    ten_thuoc:    str
    ten_hoat_chat: str
    don_vi_tinh:  str
    ham_luong:    str
    duong_dung:   str
    ma_duong_dung: str
    dang_bao_che: str
    don_gia:      Optional[float]
    don_gia_bh:   Optional[float]
    so_luong:     Optional[float]
    tt_thau:      str
    tu_ngay:      str   # DATE8
    den_ngay:     str   # DATE8, "" = còn hiệu lực
    ma_cskcb:     str
    loai_thuoc:   str   # "1"=hóa dược, "2"=YHCT
    loai_thau:    str   # "1"=TT, "2"=địa phương
    row_index:    int   # dòng trong file gốc (để trace)

    def is_valid_on(self, ngay: str) -> bool:
        """Kiểm tra entry có hiệu lực tại ngày DATE8 cho trước."""
        try:
            d = datetime.strptime(str(ngay)[:8], "%Y%m%d")
            if self.tu_ngay:
                tu = datetime.strptime(str(self.tu_ngay)[:8], "%Y%m%d")
                if d < tu:
                    return False
            if self.den_ngay:
                den = datetime.strptime(str(self.den_ngay)[:8], "%Y%m%d")
                if d > den:
                    return False
            return True
        except (ValueError, TypeError):
            return True   # không parse được → không lọc


class DanhMucThuocLoader:
    """
    Load một lần, tra cứu nhiều lần.
    Thread-safe ở mức read-only (không modify sau __init__).
    """

    def __init__(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Không tìm thấy file danh mục thuốc: {filepath}")
        self.filepath = filepath
        self._entries: list[DrugEntry] = []
        # Index 1: (ma_thuoc, so_dang_ky) → list[DrugEntry]
        self._idx_ma_sdk:   dict[tuple[str, str], list[DrugEntry]] = defaultdict(list)
        # Index 2: ma_thuoc → list[DrugEntry]
        self._idx_ma:       dict[str, list[DrugEntry]] = defaultdict(list)
        # Index 3: so_dang_ky → list[DrugEntry]
        self._idx_sdk:      dict[str, list[DrugEntry]] = defaultdict(list)
        # Set tất cả ma_thuoc hợp lệ (để check nhanh)
        self.ma_thuoc_set:  set[str] = set()
        self.so_dang_ky_set: set[str] = set()

        self._load()

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    def _load(self):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("Cần cài pandas: pip install pandas openpyxl")

        df = pd.read_excel(self.filepath, dtype=str)
        df = df.fillna("")

        for row_num, (_, row) in enumerate(df.iterrows(), start=2):  # start=2: bỏ qua header
            def g(col):
                return str(row.get(col, "")).strip()

            def gf(col) -> Optional[float]:
                v = g(col)
                try:
                    return float(v) if v else None
                except ValueError:
                    return None
            """ DUONG_DUNG trong XML đang để mã chứ không để chữ """
            entry = DrugEntry(
                ma_thuoc      = g("MA_THUOC"),
                so_dang_ky    = g("SO_DANG_KY"),
                ten_thuoc     = g("TEN_THUOC"),
                ten_hoat_chat = g("TEN_HOAT_CHAT"),
                don_vi_tinh   = g("DON_VI_TINH"),
                ham_luong     = g("HAM_LUONG"),
                duong_dung    = g("MA_DUONG_DUNG"),
                ma_duong_dung = g("MA_DUONG_DUNG"),
                dang_bao_che  = g("DANG_BAO_CHE"),
                don_gia       = gf("DON_GIA"),
                don_gia_bh    = gf("DON_GIA_BH"),
                so_luong      = gf("SO_LUONG"),
                tt_thau       = g("TT_THAU"),
                tu_ngay       = g("TU_NGAY"),
                den_ngay      = g("DEN_NGAY"),
                ma_cskcb      = g("MA_CSKCB"),
                loai_thuoc    = g("LOAI_THUOC"),
                loai_thau     = g("LOAI_THAU"),
                row_index     = row_num,
            )
            if not entry.ma_thuoc:
                continue

            self._entries.append(entry)
            self._idx_ma_sdk[(entry.ma_thuoc, entry.so_dang_ky)].append(entry)
            self._idx_ma[entry.ma_thuoc].append(entry)
            self._idx_sdk[entry.so_dang_ky].append(entry)
            self.ma_thuoc_set.add(entry.ma_thuoc)
            if entry.so_dang_ky:
                self.so_dang_ky_set.add(entry.so_dang_ky)

    # ------------------------------------------------------------------
    # Tra cứu
    # ------------------------------------------------------------------
    def lookup(
        self,
        ma_thuoc:  str | None = None,
        so_dang_ky: str | None = None,
        ngay_yl:   str | None = None,
    ) -> list[DrugEntry]:
        """
        Tra cứu danh mục thuốc.
        - Nếu có cả ma_thuoc + so_dang_ky → tìm chính xác cặp đó.
        - Nếu chỉ có ma_thuoc → tất cả dòng có cùng MA_THUOC.
        - Nếu chỉ có so_dang_ky → tất cả dòng có cùng SO_DANG_KY.
        - ngay_yl (DATE8/12): lọc thêm theo hiệu lực TU_NGAY/DEN_NGAY.
        """
        if ma_thuoc and so_dang_ky:
            results = self._idx_ma_sdk.get(
                (ma_thuoc.strip(), so_dang_ky.strip()), []
            )
        elif ma_thuoc:
            results = self._idx_ma.get(ma_thuoc.strip(), [])
        elif so_dang_ky:
            results = self._idx_sdk.get(so_dang_ky.strip(), [])
        else:
            results = self._entries

        if ngay_yl:
            ngay8 = str(ngay_yl)[:8]
            results = [e for e in results if e.is_valid_on(ngay8)]

        return results

    def in_catalog(
        self,
        ma_thuoc:   str | None = None,
        so_dang_ky: str | None = None,
        ngay_yl:    str | None = None,
    ) -> bool:
        """True nếu thuốc có trong danh mục (và còn hiệu lực tại ngày)."""
        return len(self.lookup(ma_thuoc, so_dang_ky, ngay_yl)) > 0

    @property
    def total(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return (f"DanhMucThuocLoader(file={os.path.basename(self.filepath)!r}, "
                f"entries={self.total}, ma_thuoc={len(self.ma_thuoc_set)})")