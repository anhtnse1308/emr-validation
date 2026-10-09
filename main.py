import time
from services.excel_service import ExcelService
from services.helper import FileHelper
from giamdinh.GiamDinhServices import GiamDinhService
from giamdinh.DanhMucThuocLoader import DanhMucThuocLoader
from giamdinh.rules.KiemTraThuocDanhMuc import KiemTraThuocDanhMuc
from collections import Counter
import os


# ===========================================================================
# Đường dẫn file txt cố định
# ===========================================================================
# Thư mục chứa file exe (hoặc script khi chạy .py trực tiếp)
import sys as _sys
_BASE_DIR = (
    os.path.dirname(_sys.executable)   # khi đóng gói thành .exe
    if getattr(_sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))  # khi chạy .py
)

PATH_TXT_BHYT = os.path.join(_BASE_DIR, "PATH_CHECK_XML.txt")
PATH_TXT_BQP  = os.path.join(_BASE_DIR, "PATH_CHECK_XML_BQP.txt")


def _doc_file_txt(path_txt: str) -> tuple[str, str, str]:
    """
    Đọc file txt, trả về (danh_muc_file, excel_file).
    Dòng 1: đường dẫn file danh mục thuốc
    Dòng 2: đường dẫn file danh mục DVKT MA_MAY
    Dòng 3: đường dẫn file Excel BHYT
    """
    try:
        lines = open(path_txt, encoding="utf-8-sig").read().splitlines()
    except UnicodeDecodeError:
        lines = open(path_txt, encoding="cp1252").read().splitlines()

    # Lọc bỏ dòng trống
    lines = [l.strip().strip('"').strip() for l in lines if l.strip()]

    if len(lines) < 2:
        print(f"❌ File txt thiếu dữ liệu (cần 2 dòng): {path_txt}")
        exit()

    danh_muc = lines[0]
    danh_muc_may = lines[1] if len(lines) > 1 else ""
    excel    = lines[2] if len(lines) > 2 else ""

    if not excel:
        print(f"❌ File txt thiếu dữ liệu (cần 3 dòng): {path_txt}")
        exit()

    errors = []
    if danh_muc and not os.path.exists(danh_muc):
        errors.append(f"   Danh mục thuốc : {danh_muc}")
    if danh_muc_may and not os.path.exists(danh_muc_may):
        errors.append(f"   Danh mục MA_MAY: {danh_muc_may}")
    if not os.path.exists(excel):
        errors.append(f"   Excel BHYT     : {excel}")

    if errors:
        print(f"❌ File không tồn tại:\n" + "\n".join(errors))
        exit()

    return danh_muc, danh_muc_may, excel


def _prompt_path(label: str, required: bool = True) -> str:
    """Hỏi đường dẫn file thủ công."""
    while True:
        try:
            p = input(f"{label}: ").strip().strip('"')
        except KeyboardInterrupt:
            print("\nĐã hủy chương trình.")
            exit()
        if not p and not required:
            return ""
        if os.path.exists(p):
            return p
        print("❌ File không tồn tại!")
        if not required:
            choice = input("Bỏ qua và tiếp tục không dùng danh mục? (Y/N): ").strip().lower()
            if choice == "y":
                return ""
        else:
            choice = input("Nhập lại? (Y/N): ").strip().lower()
            if choice != "y":
                print("Đã hủy chương trình.")
                exit()


# ===========================================================================
# 0. Input – Menu chọn nguồn file
# ===========================================================================
print("=" * 60)
print("  CÔNG CỤ VALIDATE & GIÁM ĐỊNH XML BHYT")
print("=" * 60)
print()
print("  Chọn nguồn file:")
print("  [1] BHYT thường        (đọc từ PATH_CHECK_XML.txt)")
print("  [2] BHYT Quân đội/QP  (đọc từ PATH_CHECK_XML_BQP.txt)")
print("  [3] Nhập tay")
print()

while True:
    try:
        chon = input("  Lựa chọn (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\nĐã hủy."); exit()

    if chon == "1":
        print(f"\n  Đọc từ: {PATH_TXT_BHYT}")
        danh_muc_file, _danh_muc_may_txt, excel_file = _doc_file_txt(PATH_TXT_BHYT)
        print(f"  Danh mục : {danh_muc_file}")
        print(f"  Excel    : {excel_file}")
        break
    elif chon == "2":
        print(f"\n  Đọc từ: {PATH_TXT_BQP}")
        danh_muc_file, _danh_muc_may_txt, excel_file = _doc_file_txt(PATH_TXT_BQP)
        print(f"  Danh mục : {danh_muc_file}")
        print(f"  Excel    : {excel_file}")
        break
    elif chon == "3":
        excel_file    = _prompt_path("Nhập file Excel BHYT")
        danh_muc_file = _prompt_path(
            "Nhập file danh mục thuốc (Enter để bỏ qua)",
            required=False,
        )
        break
    else:
        print("  ❌ Vui lòng nhập 1, 2 hoặc 3.")

# ===========================================================================
# 1. Đọc + validate dữ liệu (layer hiện có)
# ===========================================================================
print("\n" + "=" * 60)
print("  1. VALIDATE DỮ LIỆU XML")
print("=" * 60)

all_objects, _ = ExcelService.read_excel(excel_file)

FileHelper.print_errors_console(all_objects)

summary_log    = FileHelper.write_log_summary(excel_file, all_objects)
json_log       = FileHelper.write_log_json(excel_file, all_objects, suffix="errors")
errors_only_log = FileHelper.write_log_errors_only(excel_file, all_objects)
excel_summary  = FileHelper.write_excel_summary(excel_file, all_objects)
excel_errors   = FileHelper.write_excel_errors_only(excel_file, all_objects)

print(f"\n✅ Log tổng hợp      : {summary_log}")
print(f"✅ Log JSON          : {json_log}")
print(f"✅ Log lỗi           : {errors_only_log}")
print(f"✅ Excel tổng hợp    : {excel_summary}")
print(f"✅ Excel lỗi         : {excel_errors}")

# ===========================================================================
# 2. Giám định thanh toán
# ===========================================================================
print("\n" + "=" * 60)
print("  2. GIÁM ĐỊNH THANH TOÁN BHYT")
print("=" * 60)

giamdinh_errors = GiamDinhService.run(all_objects)

if giamdinh_errors:
    cnt = Counter(e.ma_ly_do for e in giamdinh_errors)
    print(f"\n⚠️  Phát hiện {len(giamdinh_errors)} trường hợp cần xem xét:")
    for ma_ly_do, so_luong in sorted(cnt.items()):
        print(f"   {(ma_ly_do or '(không có mã)'):30s}: {so_luong}")
else:
    print("\n✓ Không phát hiện trường hợp vi phạm quy định thanh toán.")

giamdinh_excel = GiamDinhService.write_excel_giamdinh(excel_file, giamdinh_errors)
print(f"\n✅ Excel giám định   : {giamdinh_excel}")

# ===========================================================================
# 3. Kiểm tra thuốc theo danh mục (nếu có file danh mục)
# ===========================================================================
print("\n" + "=" * 60)
print("  3. KIỂM TRA THUỐC THEO DANH MỤC TRÚNG THẦU")
print("=" * 60)

if not danh_muc_file:
    print("⏭  Bỏ qua (không có file danh mục).")
else:
    print(f"Đang nạp danh mục: {danh_muc_file} ...")
    loader      = DanhMucThuocLoader(danh_muc_file)
    print(f"  → {loader}")

    n_xml2 = len(all_objects.get("XML2", []))
    print(f"  → XML2: {n_xml2} dòng")

    if n_xml2 == 0:
        print("⏭  Không có dữ liệu XML2.")
    else:
        dm_errors = KiemTraThuocDanhMuc(loader).check(all_objects)

        MA_MOT_TA = {
            "WARN.DM01": "MA_THUOC không có trong danh mục",
            "WARN.DM02": "SO_DANG_KY không khớp",
            "WARN.DM03": "DON_GIA vượt DON_GIA_BH",
            "WARN.DM04": "DUONG_DUNG không khớp",
            "WARN.DM05": "HAM_LUONG không khớp",
            "WARN.DM06": "Thuốc hết hiệu lực tại ngày y lệnh",
        }

        if dm_errors:
            cnt_dm = Counter(e.ma_ly_do for e in dm_errors)
            print(f"\n⚠️  Phát hiện {len(dm_errors)} dòng cần xem xét:")
            for ma, so in sorted(cnt_dm.items()):
                print(f"   {ma:15s} ({MA_MOT_TA.get(ma, '')}): {so} dòng")
        else:
            print("\n✓ Thuốc khớp hoàn toàn với danh mục trúng thầu.")

        from run_kiem_tra_danh_muc import write_excel_danhmuc
        dm_excel = write_excel_danhmuc(excel_file, dm_errors, danh_muc_file)
        print(f"\n✅ Excel danh mục    : {dm_excel}")


# ===========================================================================
# 4. Kiểm tra ngày giường nội trú (MA_LOAI_KCB=03)
# ===========================================================================
print("\n" + "=" * 60)
print("  4. KIỂM TRA NGÀY GIƯỜNG NỘI TRÚ")
print("=" * 60)

from giamdinh.rules.KiemTraNgayGiuong import KiemTraNgayGiuong

gg_errors = KiemTraNgayGiuong().check(all_objects)

if gg_errors:
    cnt_gg = Counter(e.ma_ly_do for e in gg_errors)
    print(f"\n⚠️  Phát hiện {len(gg_errors)} trường hợp:")
    print(f"   WARN.GG01 (thiếu/thừa dịch vụ giường) : {cnt_gg.get('WARN.GG01', 0)}")
    print(f"   WARN.GG02 (trùng giường cùng ngày)    : {cnt_gg.get('WARN.GG02', 0)}")
else:
    print("\n✓ Không phát hiện lỗi ngày giường.")

gg_excel = KiemTraNgayGiuong.write_excel(excel_file, gg_errors)
print(f"\n✅ Excel ngày giường : {gg_excel}")


# ===========================================================================
# 5. Sàng lọc mã đối tượng KCB
# ===========================================================================
print("\n" + "=" * 60)
print("  5. SÀNG LỌC MÃ ĐỐI TƯỢNG KCB")
print("=" * 60)

from giamdinh.rules.SangLocDoiTuong import SangLocDoiTuong

dt_errors = SangLocDoiTuong().check(all_objects)

if dt_errors:
    cnt_dt = Counter(e.ma_ly_do for e in dt_errors)
    print(f"\n⚠️  Phát hiện {len(dt_errors)} trường hợp:")
    MA_TEN = {
        "WARN.DT01": "1.14 ≠ ngoại trú",
        "WARN.DT02": "1.15 ≠ nội trú",
        "WARN.DT03": "DKBD=74021 nhưng đối tượng sai",
        "WARN.DT04": "DKBD≠74021 nhưng đối tượng/giấy CT sai",
        "WARN.DT05": "1.7 sơ sinh vượt 5 ngày",
    }
    for ma, so in sorted(cnt_dt.items()):
        print(f"   {ma:12s} ({MA_TEN.get(ma,'')}): {so}")
else:
    print("\n✓ Không phát hiện vi phạm mã đối tượng KCB.")

dt_excel = SangLocDoiTuong.write_excel(excel_file, dt_errors)
print(f"\n✅ Excel đối tượng  : {dt_excel}")


# ===========================================================================
# 6. Kiểm tra MA_MAY theo danh mục DVKT yêu cầu khai báo máy
# ===========================================================================
print("\n" + "=" * 60)
print("  6. KIỂM TRA MA_MAY DVKT")
print("=" * 60)

from giamdinh.rules.KiemTraMaMay import DanhMucMaMayLoader, KiemTraMaMay

# Dùng từ file txt nếu có (option 1/2), fallback hỏi tay (option 3)
_danh_muc_may_file = (
    _danh_muc_may_txt
    if "_danh_muc_may_txt" in dir() and _danh_muc_may_txt
    else _prompt_path(
        "Nhập file danh mục DVKT cần MA_MAY (Enter để bỏ qua)",
        required=False,
    )
)

if not _danh_muc_may_file:
    print("⏭  Bỏ qua.")
else:
    print(f"Đang nạp danh mục: {_danh_muc_may_file} ...")
    _loader_may = DanhMucMaMayLoader(_danh_muc_may_file)
    print(f"  → {_loader_may}")

    _mm_errors = KiemTraMaMay(_loader_may).check(all_objects)

    if _mm_errors:
        print(f"\n⚠️  Phát hiện {len(_mm_errors)} dòng DVKT thiếu MA_MAY.")
    else:
        print("\n✓ Tất cả DVKT yêu cầu MA_MAY đều đã khai báo.")

    _mm_excel = KiemTraMaMay.write_excel(excel_file, _mm_errors)
    print(f"\n✅ Excel MA_MAY       : {_mm_excel}")

# ===========================================================================
print("\n" + "=" * 60)
print("  HOÀN TẤT")
print("=" * 60)

for i in range(5, 0, -1):
    print(f"Đóng sau {i} giây...")
    time.sleep(1)
print("Tạm biệt!")