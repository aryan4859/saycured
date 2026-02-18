from django.test import TestCase
from django.urls import reverse
from .models import ScanHistory, Domain

class ScanEngineTestCase(TestCase):
    def setUp(self):
        # Create a sample domain
        self.domain = Domain.objects.create(name="example.com")
        # Create a sample scan history
        self.scan = ScanHistory.objects.create(
            domain=self.domain,
            status="PENDING"
        )

    def test_domain_creation(self):
        """Test if domain is created successfully"""
        self.assertEqual(self.domain.name, "example.com")
        self.assertTrue(isinstance(self.domain, Domain))

    def test_scan_history_creation(self):
        """Test if scan history record is created"""
        self.assertEqual(self.scan.domain.name, "example.com")
        self.assertEqual(self.scan.status, "PENDING")

    def test_scan_start_endpoint(self):
        """Test starting a scan via API"""
        url = reverse('start_scan')  # Your API endpoint name
        response = self.client.post(url, {'domain': self.domain.name})
        self.assertEqual(response.status_code, 200)
        self.assertIn('scan_id', response.json())

    def test_scan_results_endpoint(self):
        """Test fetching scan results via API"""
        url = reverse('scan_results', args=[self.scan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
