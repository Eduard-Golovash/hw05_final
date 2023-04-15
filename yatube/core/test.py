from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_custom_403(self):
        response = self.client.get('login')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'core/403csrf.html')
