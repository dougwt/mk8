"""Unit tests for comparison.views."""

from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import Client, TestCase

from .models import ConfigList, ConfigListItem, KartConfig


class ViewTestCase(TestCase):
    """Tests for non-populated list views."""
    fixtures = [
        'racer.json',
        'racerstats.json',
        'body.json',
        'tire.json',
        'glider.json',
    ]

    def setUp(self):
        """Establish a test client for each test."""
        self.client = Client()

    def test_home(self):
        """Ensure home view renders."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Ensure Add Configuration modals are present
        self.assertTrue('id="addModalDriver"' in response.content)
        self.assertTrue('id="addModalKart"' in response.content)
        self.assertTrue('id="addModalTire"' in response.content)
        self.assertTrue('id="addModalGlider"' in response.content)

        # Ensure context variables exist
        self.assertTrue(response.context['racerstats'])
        self.assertTrue(response.context['racers'])
        self.assertTrue(response.context['bodies'])
        self.assertTrue(response.context['tires'])
        self.assertTrue(response.context['gliders'])
        self.assertEqual(len(response.context['configurations']), 0)
        self.assertEqual(response.context['total_list_count'], 0)
        self.assertEqual(response.context['total_config_count'], 0)

    def test_home_add(self):
        """Ensure home view processes list addition."""
        response = self.client.post('/', {
            'add-racer': 10,
            'add-body': 19,
            'add-tire': 2,
            'add-glider': 2,
        })
        self.assertTrue(response.status_code, 200)

        # Ensure context variables exist
        self.assertEqual(len(response.context['configurations']), 1)

    def test_home_add_duplicate(self):
        """Ensure home view processes list addition."""
        response = self.client.post('/', {
            'add-racer': 10,
            'add-body': 19,
            'add-tire': 2,
            'add-glider': 2,
        })
        self.assertTrue(response.status_code, 200)

        # Ensure context variables exist
        self.assertEqual(len(response.context['configurations']), 1)

        # Attempt to add duplicate
        response = self.client.post('/', {
            'add-racer': 10,
            'add-body': 19,
            'add-tire': 2,
            'add-glider': 2,
        })
        self.assertTrue(response.status_code, 200)

        # Ensure no new config was added
        self.assertEqual(len(response.context['configurations']), 1)

        # Ensure warning message appears
        exists_msg = 'The configuration you added already exists in your list.'
        self.assertTrue(exists_msg in response.content)

    def test_components(self):
        """Ensure components view renders."""
        response = self.client.get(reverse('components'))
        self.assertEqual(response.status_code, 200)

        # Ensure Component tabs are present
        self.assertTrue('id="kart-racer"' in response.content)
        self.assertTrue('id="kart-body"' in response.content)
        self.assertTrue('id="kart-tire"' in response.content)
        self.assertTrue('id="kart-glider"' in response.content)

        # Ensure context variables exist
        self.assertTrue(response.context['racerstats'])
        self.assertTrue(response.context['racers'])
        self.assertTrue(response.context['bodies'])
        self.assertTrue(response.context['tires'])
        self.assertTrue(response.context['gliders'])
        self.assertEqual(response.context['total_list_count'], 0)
        self.assertEqual(response.context['total_config_count'], 0)

    def test_reset(self):
        """Ensure reset view empties list and redirects."""
        # Ensure configurations is empty
        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['configurations']), 0)

        # Add a configuration
        response = self.client.post('/', {
            'add-racer': 10,
            'add-body': 19,
            'add-tire': 2,
            'add-glider': 2,
        })
        response = self.client.get(reverse('home'))

        # Ensure configuration is not empty
        self.assertEqual(len(response.context['configurations']), 1)

        # Reset configurations
        response = self.client.get(reverse('reset'))
        self.assertEqual(response.status_code, 302)

        # Ensure configurations is empty
        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['configurations']), 0)

    def test_list_404(self):
        """Ensure list view returns 404 for invalid url hash."""
        response = self.client.get(reverse('list', kwargs={
            'url_hash': 'fffff',
        }))
        self.assertEqual(response.status_code, 404)

    def test_save_empty(self):
        """Ensure save view handles empty save."""
        response = self.client.get(reverse('save'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            'Your current list has been saved to' in response.content
        )

    def test_top_empty(self):
        """Ensure top view renders."""
        response = self.client.get(reverse('top'))
        self.assertEqual(response.status_code, 200)

        # Ensure context variables exist
        self.assertEqual(len(response.context['popular_lists']), 0)


class PopulatedListViewTestCase(TestCase):
    """Tests for populated list views."""
    fixtures = [
        'racer.json',
        'racerstats.json',
        'body.json',
        'tire.json',
        'glider.json',
    ]

    def setUp(self):
        """Establish a test client with ConfigList and ConfigListItems."""
        self.client = Client()

        # Initialize mock request
        mock_request = HttpRequest()
        mock_request.META = {
            'HTTP_X_REAL_IP': '127.0.0.1',
            'REMOTE_ADDR': '172.31.233.133',
        }

        # Create a ConfigList
        self.assertEqual(len(ConfigList.objects.all()), 0)
        self.config_list = ConfigList.create(mock_request)
        self.config_list.save()
        self.assertEqual(len(ConfigList.objects.all()), 1)

        # Create multiple ConfigListItems
        self.assertEqual(len(ConfigListItem.objects.all()), 0)
        test_kart_ids = (
            (8, 19, 2, 2),  # Shyguy
            (9, 2, 14, 2),  # Koopa Troopa
        )
        for kart in test_kart_ids:
            config = KartConfig(kart)
            ConfigListItem.create(
                self.config_list,
                config.racer,
                config.body,
                config.tire,
                config.glider
            ).save()
        self.assertEqual(len(ConfigListItem.objects.all()), 2)

    def test_list(self):
        """Ensure list view renders valid url hash."""
        # Request response for newly created list page
        response = self.client.get(reverse('list', kwargs={
            'url_hash': self.config_list.url,
        }))
        self.assertEqual(response.status_code, 200)

        # Ensure context variables exist
        self.assertTrue(response.context['racerstats'])
        self.assertTrue(response.context['racers'])
        self.assertTrue(response.context['bodies'])
        self.assertTrue(response.context['tires'])
        self.assertTrue(response.context['gliders'])
        self.assertTrue(response.context['configurations'])
        self.assertEqual(response.context['total_list_count'], 1)
        self.assertEqual(response.context['total_config_count'], 2)

    def test_save(self):
        """Ensure save view exports list."""
        response = self.client.get(reverse('save'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            'Your current list has been saved to' in response.content
        )

    def test_top_populated(self):
        """Ensure top view renders."""
        response = self.client.get(reverse('top'))
        self.assertEqual(response.status_code, 200)

        # Ensure context variables exist
        self.assertEqual(len(response.context['popular_lists']), 1)
