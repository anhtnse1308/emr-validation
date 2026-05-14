from model.XML1 import Bang1_TongHop
from model.XML10 import Bang10_GiayNghiDuongThai
from model.XML11 import Bang11_GiayNghiHuongBHXH
from model.XML13 import Bang13_GiayChuyenTuyen
from model.XML14 import Bang14_GiayHenKhamLai
from model.XML2 import Bang2_Thuoc
from model.XML3 import Bang3_DVKT_VTYT
from model.XML4 import Bang4_DichVuCLS
from model.XML5 import Bang5_DienBienLamSang
from model.XML7 import Bang7_GiayRaVien
from model.XML8 import Bang8_TomTatHSBA
from model.XML9 import Bang9_GiayChungSinh
from services.excel_service import ExcelService
from services.helper import FileHelper
import os

while True:

    excel_file = input("Nhập file Excel: ").strip().strip('"')

    if os.path.exists(excel_file):
        break

    choice = input(
        "❌ File không tồn tại! Nhập lại? (Y/N): "
    ).strip().lower()

    if choice != "y":

        print("Đã hủy chương trình.")

        exit()

all_objects, all_errors = ExcelService.read_excel(excel_file)

# --- In ra console ---
FileHelper.print_errors_console(all_objects)

# --- Ghi log tổng hợp text (y chang console) ---
summary_log = FileHelper.write_log_summary(excel_file, all_objects)
print(f"\n✅ Đã ghi log tổng hợp : {summary_log}")

# --- Ghi log JSON kèm dữ liệu dòng lỗi ---
json_log = FileHelper.write_log_json(excel_file, all_objects, suffix="errors")
print(f"✅ Đã ghi log JSON chi tiết: {json_log}")

# --- Ghi log txt CHỈ chứa dòng lỗi ---
errors_only_log = FileHelper.write_log_errors_only(excel_file, all_objects)
print(f"✅ Đã ghi log lỗi tổng hợp: {errors_only_log}")