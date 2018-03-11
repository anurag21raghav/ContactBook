from django.test import TestCase
from ContactBookApp.models import Contact
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

# models test
class ContactModelTestCase(TestCase):
    """
    This class defines the test suite for the contact model.
    """

    def setUp(self):
        self.contact_name = 'test'
        self.contact_email = 'test@test.com'
        user = User.objects.create(username="test")
        self.contact = Contact(name=self.contact_name, email=self.contact_email, owner=user)

    def test_model_can_create_a_contact(self):
        """Test the contact model can create a contact."""
        old_count = Contact.objects.count()
        self.contact.save()
        new_count = Contact.objects.count()
        self.assertNotEqual(old_count, new_count)

class IndexViewTestCase(TestCase):
    """Test suite for the `/` api views."""

    def setUp(self):
        user = User.objects.create(username="test")
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        self.contact_data = {'name': 'Test', 'email':'test@test.com', 'owner_id': user.pk}
        self.response = self.client.post(
            reverse('index'),
            self.contact_data,
            format="json")

    def test_api_can_create_a_contact(self):
        """Test the api has contact creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_get_a_contact(self):
        """Test the api can get a given contact."""
        contactlist = Contact.objects.get()
        response = self.client.get(
            reverse('index',), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, contactlist)

    def test_api_can_update_contact(self):
        """Test the api can update a given contact."""
        change_contactlist = {'name': 'Test1', 'email':'test@test.com'}
        res = self.client.put(
            reverse('index',),
            change_contactlist, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_contact(self):
        """Test the api can delete a contact."""
        contactlist = Contact.objects.get()
        change_contactlist = {'email':'test@test.com'}
        response = self.client.delete(
            reverse('index',),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

class SearchViewTestCase(TestCase):
    """Test suite for the `/search` api views."""

    def setUp(self):
        user = User.objects.create(username="test")
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        key = {'key':'test'}
        self.response = self.client.get(
            reverse('search',),
            key,
            format="json")

    def test_api_can_search_a_contact(self):
        """Test the api has contact search capability."""
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)