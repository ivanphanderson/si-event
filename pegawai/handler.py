from abc import ABC, abstractmethod
from typing import List, Dict


class DataHandler(ABC):
    def __init__(self, next_handler):
        self.next_handler: DataHandler = next_handler

    @abstractmethod
    def functionality(self, data: List[List[str]], information: Dict[str, str]):
        """This method will be implemented by its subclass as the chain's functionality"""


class DataCleaner(DataHandler):
    def functionality(self, data: List[List[str]], information: Dict[str, str]):
        """
        Clean the data (for now remove leading and trailing whitespaces)
        """
        super().functionality(data, information)
        for row in range(len(data)):
            record = data[row]
            for col in range(len(record)):
                record[col] = str(record[col]).strip()
        last_records_index = self.get_last_records_index(data)

        if self.next_handler is not None:
            return self.next_handler.functionality(
                data[: last_records_index + 1], information
            )
        return [data, information]

    def get_last_records_index(self, data: List[List[str]]):
        """
        Get index of last records
        """
        last_index = len(data) - 1
        while True:
            if data[last_index][0].strip() != "":
                break
            last_index -= 1
        return last_index


class ValidColumnNameChecker(DataHandler):
    def __init__(self, next_handler):
        self.next_handler: DataHandler = next_handler
        self.valid_columns = [
            "no",
            "employee no.",
            "employee name",
            "employee category",
            "job status",
            "grade level",
            "employment status",
            "email",
            "nama di rekening",
            "nama bank",
            "no rekening",
            "nomor npwp",
            "alamat npwp",
        ]

    def functionality(self, data: List[List[str]], information: Dict[str, str]):
        """
        Make sure that columns is valid and in correct order
        """
        super().functionality(data, information)
        records_index = self.get_records_index(data)
        information["records_index"] = records_index

        header_row = data[records_index - 1]
        for i in range(len(header_row)):
            if header_row[i].lower() != self.valid_columns[i]:
                raise TypeError(
                    f"*Terdeteksi kolom {header_row[i]} tidak sesuai, bisa posisi atau namanya!"
                )
        return self.next_handler.functionality(data, information)

    def get_records_index(self, data: List[List[str]]):
        """
        Return index of data records (not header)
        """
        try:
            index_start_data = 0
            while True:
                if data[index_start_data][0].lower().strip() == "no":
                    index_start_data += 1
                    break
                index_start_data += 1
            return index_start_data
        except IndexError:
            raise TypeError("Invalid Data Format!")


class UniqueEmailInFileChecker(DataHandler):
    def functionality(self, data: List[List[str]], information: Dict[str, str]):
        """
        Check if all emails in uploaded file is unique
        """
        super().functionality(data, information)
        unique_emails = set()
        records_in_data = data[information["records_index"] :]

        for index in range(len(records_in_data)):
            unique_emails.add(records_in_data[index][7])

        if len(unique_emails) == len(records_in_data):
            return [data, information]

        raise TypeError("Email must be Unique!")
