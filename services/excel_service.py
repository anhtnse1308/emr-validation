import pandas as pd 
from model.XML1 import Bang1_TongHop 
from model.XML2 import Bang2_Thuoc 
from model.XML3 import Bang3_DVKT_VTYT 
from model.XML4 import Bang4_DichVuCLS 
from model.XML5 import Bang5_DienBienLamSang  
from model.XML7 import Bang7_GiayRaVien 
from model.XML8 import Bang8_TomTatHSBA 
from model.XML9 import Bang9_GiayChungSinh 
from model.XML10 import Bang10_GiayNghiDuongThai 
from model.XML11 import Bang11_GiayNghiHuongBHXH 
from model.XML13 import Bang13_GiayChuyenTuyen
from model.XML14 import Bang14_GiayHenKhamLai

# Mapping tên sheet -> class
SHEET_CLASS_MAP = {
    "XML1": Bang1_TongHop,
    "XML2": Bang2_Thuoc,
    "XML3": Bang3_DVKT_VTYT,
    "XML4": Bang4_DichVuCLS,
    "XML5": Bang5_DienBienLamSang,
    "XML7": Bang7_GiayRaVien,
    "XML8": Bang8_TomTatHSBA,
    "XML9": Bang9_GiayChungSinh,
    "XML10": Bang10_GiayNghiDuongThai,
    "XML11": Bang11_GiayNghiHuongBHXH,
    "XML13": Bang13_GiayChuyenTuyen,
    "XML14": Bang14_GiayHenKhamLai,
}
#XML6, XML12 không nằm trong file hiện tại của bệnh viện

class ExcelService:

    @staticmethod
    def read_excel(excel_file):

        all_sheets = pd.read_excel(
            excel_file,
            sheet_name=None,
            dtype=str
        )

        all_objects = {}

        all_errors = set()

        for sheet_name, df in all_sheets.items():

            if sheet_name not in SHEET_CLASS_MAP:
                continue

            model_class = SHEET_CLASS_MAP[sheet_name]

            objects = []

            df = df.fillna("")

            for excel_row, (_, row) in enumerate(df.iterrows(), start=2):

                row_dict = row.to_dict()

                obj = model_class.from_dict(row_dict)

                errors = obj.validate()

                if errors:

                    for err in errors:

                        all_errors.add(
                            f"{sheet_name} - Row {excel_row} - {err}"
                        )

                objects.append(obj)

            all_objects[sheet_name] = objects
        print("\nĐọc dữ liệu hoàn tất")
        return all_objects, all_errors