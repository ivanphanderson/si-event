from io import BytesIO
import xlsxwriter


class StandardExcel:
    def get_excel(self, table_data):
        excel_file = BytesIO()
        workbook = xlsxwriter.Workbook(excel_file)
        worksheet = workbook.add_worksheet()

        ws_row = 0
        ws_col = 0

        for row_accessor in table_data.keys():
            row_data = table_data[row_accessor]
            for col_accessor in row_data.keys():
                if (col_accessor == 'total bruto'):
                    ws_col += 2
                worksheet.write(ws_row, ws_col, row_data[col_accessor])
                ws_col += 1
            ws_row += 1
            ws_col = 0
        
        workbook.close()
        excel_file.seek(0)
        return excel_file


class BTRMemoExcel:
    def get_excel(self, table_data):
        excel_file = BytesIO()
        workbook = xlsxwriter.Workbook(excel_file)

        KOORDINATOR_SDM = 'Hennie Marianie, S.E., MSM'
        PIHAK_SDM = 'Amala Kusumaputri'
        memo = workbook.add_worksheet(name='memo')
        ws_col = 0

        memo.merge_range("A6:H6", 'MEMO', cell_format=workbook.add_format({'bold': True, 'font_size': 22, 'bg_color': 'gray'}))
        memo.write_string(7, ws_col, 'TANGGAL', cell_format=workbook.add_format({'top': 1, 'bottom': 1}))
        for i in range(1, 8):
            memo.write_string(7, ws_col+i, '', cell_format=workbook.add_format({'top': 1, 'bottom': 1}))
        memo.write_string(8, ws_col, 'KEPADA')
        memo.write_string(8, ws_col+1, f'Koordinator SDM {KOORDINATOR_SDM}')
        memo.write_string(9, ws_col, 'DARI')
        memo.write_string(9, ws_col+1, PIHAK_SDM)
        memo.write_string(10, ws_col, 'PERIHAL')
        memo.write_string(10, ws_col+1, 'Permohonan pengajuan dana untuk ...')

        memo.write_string(13, ws_col, 'Ibu Hennie Yth.')
        memo.write_string(15, ws_col, 'Sehubungan dengan ...')
        memo.merge_range("A16:I20", 'Sehubungan dengan ...')

        memo.write_string(21, ws_col, 'Demikian  kami sampaikan, mohon persetujuannya. Terima kasih.')

        memo.write_string(24, ws_col, 'Menyetujui,')
        memo.write_string(25, ws_col, 'Koordinator SDM,')
        memo.write_string(25, ws_col+6, 'SDM')

        memo.write_string(30, ws_col, KOORDINATOR_SDM)
        memo.write_string(30, ws_col+6, PIHAK_SDM)

        daftar_pembayaran = workbook.add_worksheet(name='daftar pembayaran')
        daftar_pembayaran.merge_range("A1:K1", 'Daftar Pembayaran Honor', cell_format=workbook.add_format({'font_size': 14, 'align': 'center'}))
        daftar_pembayaran.merge_range("A2:K2", '(Panitia dan Tanggal)', cell_format=workbook.add_format({'font_size': 14, 'align': 'center'}))
        daftar_pembayaran.merge_range("A3:K3", 'Fakultas Ilmu Komputer Universitas Indonesia ', cell_format=workbook.add_format({'font_size': 14, 'align': 'center'}))

        ws_row = 4

        for row_accessor in table_data.keys():
            cell_format = workbook.add_format()
            if row_accessor == "0":
                cell_format.set_bg_color('gray')
                cell_format.set_font_size(14)
                cell_format.set_bold(True)
            cell_format.set_border()

            row_data = table_data[row_accessor]
            for col_accessor in row_data.keys():
                if (col_accessor == 'total bruto'):
                    ws_col += 2
                if (col_accessor == 'total'):
                    daftar_pembayaran.merge_range(f"A{ws_row+1}:C{ws_row+1}", row_data[col_accessor], cell_format)
                else:
                    daftar_pembayaran.write_string(ws_row, ws_col, row_data[col_accessor], cell_format)
                ws_col += 1
            ws_row += 1
            ws_col = 0
        
        daftar_pembayaran.write_string(ws_row+3, ws_col+1, 'Mengetahui,')
        daftar_pembayaran.write_string(ws_row+4, ws_col+1, 'Koordinator SDM')
        daftar_pembayaran.write_string(ws_row+11, ws_col+1, '(Hennie Marianie, M.SM.)')

        workbook.close()
        excel_file.seek(0)

        return excel_file

def excel_factory(type="standard"):
    types = {
        "standard": StandardExcel,
        "btrmemo": BTRMemoExcel
    }

    return types[type]()
