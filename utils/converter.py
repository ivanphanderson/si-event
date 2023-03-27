import csv
from io import StringIO
import xlrd


def get_file_content_excel(bytes_file):
    workbook = xlrd.open_workbook(file_contents=bytes_file)
    sheet = workbook.sheet_by_index(0)

    file_content = []
    for row in range(sheet.nrows):
        datum = []
        for col in range(sheet.ncols):
            datum.append(sheet.cell_value(row,col))
        file_content.append(datum)
    return file_content

def convert_to_data(bytes_file):
    try:
        file_content = get_file_content_excel(bytes_file)
        return file_content
    except xlrd.XLRDError:
        try:
            decoded_file = bytes_file.decode()
            file = StringIO(decoded_file)
            csv_data = csv.reader(file, delimiter=",")
            file_content = []
            for datum in csv_data:
                file_content.append(datum)
            return file_content
        except UnicodeDecodeError:
            raise TypeError("Incorrect Data Format, Excel or CSV only!")
