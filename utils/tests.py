from django.test import TestCase
from .converter import convert_to_data

class ConverterTest(TestCase):

    def test_convert_to_data_csv(self):
        bytes_file = b'satu,dua,tiga\nempat,lima,enam'
        expected_result = [['satu', 'dua', 'tiga'], ['empat', 'lima', 'enam']]
        actual_result = convert_to_data(bytes_file)
        self.assertListEqual(expected_result, actual_result)
