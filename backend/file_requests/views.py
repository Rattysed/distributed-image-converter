from django.http import JsonResponse, HttpResponseNotFound

from django.shortcuts import render, get_object_or_404


from .models import Request, UploadedFile, UploadedFile, EditedFile
from tasks import task_image_edit, task_to_zip
from celery import chord, group

from django.views.generic.edit import FormView
from .forms import FileFieldForm
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .serializers import RequestSerializer


def get_task_status(request_id):
    return Request.is_request_done(request_id)


def index_view(request):
    form = FileFieldForm()
    return render(request, 'upload_images.html', {'form': form})


def request_page_view(request, request_id):
    try:
        if Request.get_request(request_id) is None:
            return HttpResponseNotFound("404, No request")
    except Exception as e:
        return HttpResponseNotFound("404, No request")
        
    return render(request, 'request.html', {'request_id': request_id})


def get_request_time_processing_info(request, request_id):
    stats = {}
    try:
        req = Request.get_request(request_id)
        if req is None:
            return HttpResponseNotFound("404, No request")

        stats['seconds'] = req.get_processing_time()
    except Exception as e:
        return HttpResponseNotFound("404, No request")

    return JsonResponse(stats)


class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, format=None):
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        req = Request.create_request()
        file_ids = []
        
        for file in files:
            if file.name.endswith('.jpg') or file.name.endswith('.jpeg') or file.name.endswith('.png'):
                file_ids.append(UploadedFile.create_file(req, file.name, file).id)
            else:
                continue
                
        if not file_ids:
            return Response({'error': 'No valid image files were uploaded'}, status=status.HTTP_400_BAD_REQUEST)
                
        tasks = group(task_image_edit.s(file_id) for file_id in file_ids)
        chord(tasks)(task_to_zip.s())
        
        serializer = RequestSerializer(req)
        response_data = serializer.data
        response_data.update({
            'status_url': f'/api/status/{str(req.id)}/'
        })
        
        return Response(response_data, status=status.HTTP_202_ACCEPTED)


class RequestStatusAPIView(APIView):
    def get(self, request, request_id, format=None):
        try:
            task = Request.get_request(request_id)
            serializer = RequestSerializer(task)
            response_data = serializer.data
            
            if task.status == 'done':
                url = task.get_resulting_link()
                response_data.update({
                    'status': 'ready',
                    'link': f'{url}'
                })
            else:
                response_data.update({
                    'status': 'processing',
                })
                
            return Response(response_data)
        except ObjectDoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'pending', 'message': str(e)})
