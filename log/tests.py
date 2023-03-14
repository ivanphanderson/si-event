from django.test import TestCase


class DisplayLogTest(TestCase):

    def test_display_log_template(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log.html')
        self.assertContains(response, '<h4 style="text-align: center;">Log</h4>', status_code=200)
