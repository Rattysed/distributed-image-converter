import os
import uuid
from unittest.mock import patch, MagicMock
from io import BytesIO

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Request, UploadedFile, EditedFile, RequestStatus
from tasks import task_image_edit, task_to_zip, task_clear_requests


class ModelTests(TestCase):
    def test_request_create(self):
        request = Request.create_request()
        self.assertIsNotNone(request.id)
        self.assertEqual(request.status, RequestStatus.WAITING)
        self.assertIsNone(request.time_end)
        self.assertIsNone(request.url)
        self.assertIsNone(request.expiration_date)

    def test_request_get(self):
        request = Request.create_request()
        retrieved = Request.get_request(str(request.id))
        self.assertEqual(request.id, retrieved.id)

    def test_request_is_done(self):
        request = Request.create_request()
        self.assertFalse(Request.is_request_done(str(request.id)))

        request.status = RequestStatus.DONE
        request.save()
        self.assertTrue(Request.is_request_done(str(request.id)))

    @patch("file_requests.models.RESULT_STORAGE")
    def test_request_update_status_done(self, mock_storage):
        request = Request.create_request()
        request.update_status_done()
        self.assertEqual(request.status, RequestStatus.DONE)

    def test_request_update_expiration_date(self):
        request = Request.create_request()
        self.assertIsNone(request.expiration_date)

        request.update_expiration_date()
        self.assertIsNotNone(request.expiration_date)
        self.assertGreater(request.expiration_date, timezone.now())


class UploadedFileTests(TestCase):
    def setUp(self):
        self.request = Request.create_request()
        self.test_image = SimpleUploadedFile(
            name="test.jpg", content=b"file_content", content_type="image/jpeg"
        )

    def test_uploaded_file_create(self):
        uploaded_file = UploadedFile.create_file(
            self.request, "test.jpg", self.test_image
        )
        self.assertIsNotNone(uploaded_file.id)
        self.assertEqual(uploaded_file.request, self.request)
        self.assertEqual(uploaded_file.uploaded_name, "test.jpg")
        self.assertEqual(uploaded_file.status, RequestStatus.WAITING)


class ApiTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse("api_upload")
        self.test_image = SimpleUploadedFile(
            name="test.jpg", content=b"file_content", content_type="image/jpeg"
        )

    @patch("file_requests.views.group")
    @patch("file_requests.views.chord")
    def test_file_upload_api(self, mock_chord, mock_group):
        mock_group_instance = MagicMock()
        mock_group.return_value = mock_group_instance
        mock_chord.return_value = MagicMock()

        response = self.client.post(
            self.upload_url, {"files": [self.test_image]}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("id", response.data)
        self.assertIn("status", response.data)
        self.assertIn("status_url", response.data)

        mock_group.assert_called_once()
        mock_chord.assert_called_once()

    def test_file_upload_api_no_files(self):
        response = self.client.post(self.upload_url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_request_status_api(self):
        request = Request.create_request()
        status_url = reverse("api_status", args=[str(request.id)])

        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

        request.status = RequestStatus.DONE
        request.save()

        with patch("file_requests.models.Request.get_resulting_link") as mock_link:
            mock_link.return_value = "/test/link"
            response = self.client.get(status_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["status"], "ready")
            self.assertEqual(response.data["link"], "/test/link")

    def test_request_status_api_not_found(self):
        status_url = reverse("api_status", args=[str(uuid.uuid4())])
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class WebViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upload_images.html")
        self.assertIsNotNone(response.context["form"])

    def test_request_page_view_valid(self):
        request = Request.create_request()
        response = self.client.get(reverse("request_page", args=[str(request.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "request.html")
        self.assertEqual(response.context["request_id"], str(request.id))

    def test_request_page_view_invalid(self):
        response = self.client.get(reverse("request_page", args=[str(uuid.uuid4())]))
        self.assertEqual(response.status_code, 404)


class CeleryTasksTests(TestCase):
    def setUp(self):
        self.request = Request.create_request()
        self.test_image = SimpleUploadedFile(
            name="test.jpg", content=b"file_content", content_type="image/jpeg"
        )
        self.uploaded_file = UploadedFile.create_file(
            self.request, "test.jpg", self.test_image
        )

    @patch("file_requests.cutom_image_handler.ImageHandler.edit")
    @patch("file_requests.models.EditedFile.create_file")
    def test_task_image_edit(self, mock_create_file, mock_edit):
        mock_edit.return_value = b"edited_content"
        mock_edited_file = MagicMock()
        mock_edited_file.id = uuid.uuid4()
        mock_create_file.return_value = mock_edited_file

        result = task_image_edit(str(self.uploaded_file.id))

        self.assertEqual(result, (mock_edited_file.id, True))
        mock_edit.assert_called_once()
        mock_create_file.assert_called_once()

    @patch("file_requests.models.EditedFile.get_by_id")
    @patch("file_requests.models.Request.update_file")
    @patch("file_requests.models.Request.update_status_done")
    @patch("file_requests.models.Request.update_expiration_date")
    def test_task_to_zip(
        self,
        mock_update_expiration,
        mock_update_status,
        mock_update_file,
        mock_get_by_id,
    ):
        edited_file_id = uuid.uuid4()
        mock_edited_file = MagicMock()
        mock_edited_file.request = self.request
        mock_edited_file.file.name = "test_edited.jpg"
        mock_edited_file.get_file_data.return_value = b"edited_content"
        mock_get_by_id.return_value = mock_edited_file

        result = task_to_zip([(edited_file_id, True)])

        self.assertTrue(result)
        mock_update_file.assert_called_once()
        mock_update_status.assert_called_once()
        mock_update_expiration.assert_called_once()

    def test_task_clear_requests(self):
        Request.objects.all().delete()

        now = timezone.now()

        past = now - timezone.timedelta(days=1)

        future = now + timezone.timedelta(hours=1)

        request_expired = Request.create_request()
        Request.objects.filter(id=request_expired.id).update(expiration_date=past)

        request_valid = Request.create_request()
        Request.objects.filter(id=request_valid.id).update(expiration_date=future)

        request_none = Request.create_request()

        self.assertEqual(Request.objects.count(), 3)

        mock_now = MagicMock(return_value=now)
        with patch("django.utils.timezone.now", mock_now):
            result = task_clear_requests()

            self.assertTrue(result)

            self.assertEqual(Request.objects.count(), 2)
            with self.assertRaises(Request.DoesNotExist):
                Request.objects.get(id=request_expired.id)

            request_none_updated = Request.objects.get(id=request_none.id)
            self.assertIsNotNone(request_none_updated.expiration_date)

            self.assertIsNotNone(Request.objects.get(id=request_valid.id))


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("file_requests.views.group")
    @patch("file_requests.views.chord")
    def test_full_upload_workflow(self, mock_chord, mock_group):
        mock_group_instance = MagicMock()
        mock_group.return_value = mock_group_instance
        mock_chord.return_value = MagicMock()

        test_image = SimpleUploadedFile(
            name="test.jpg", content=b"file_content", content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("api_upload"), {"files": [test_image]}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        request_id = response.data["id"]

        response = self.client.get(reverse("api_status", args=[request_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "processing")

        request = Request.get_request(request_id)
        request.status = RequestStatus.DONE
        request.save()

        with patch("file_requests.models.Request.get_resulting_link") as mock_link:
            mock_link.return_value = "/test/result.zip"
            response = self.client.get(reverse("api_status", args=[request_id]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["status"], "ready")
            self.assertEqual(response.data["link"], "/test/result.zip")
