from services.excel_service import ExcelService
from services.helper import FileHelper
from giamdinh.GiamDinhServices import GiamDinhService
from giamdinh.DanhMucThuocLoader import DanhMucThuocLoader
from giamdinh.rules.KiemTraThuocDanhMuc import KiemTraThuocDanhMuc
from collections import Counter
import os


# ===========================================================================
# Helper prompt
# ===========================================================================
def _prompt_path(label: str, required: bool = True) -> str:
    """Hỏi đường dẫn file, lặp đến khi hợp lệ hoặc bỏ qua (nếu không bắt buộc)."""
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
# 0. Input
# ===========================================================================
print("=" * 60)
print("  CÔNG CỤ VALIDATE & GIÁM ĐỊNH XML BHYT")
print("=" * 60)

excel_file    = _prompt_path("Nhập file Excel BHYT")
danh_muc_file = _prompt_path(
    "Nhập file danh mục thuốc (Enter để bỏ qua)",
    required=False,
)

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
print("\n" + "=" * 60)
print("  HOÀN TẤT")
print("=" * 60)

while True:
    if input("Nhấn Enter để thoát...") == "":
        break
#pyinstaller --onefile --console --name EMRValidation --collect-submodules giamdinh --collect-submodules services main.py