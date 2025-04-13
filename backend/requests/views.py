from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Request
from tasks import task1


class RequestView(APIView):
    def get(self, request):
        requests = Request.objects.all()
        return Response({"requests": [str(request) for request in requests]})


class TestingView(APIView):
    def get(self, request):
        requests = Request.objects.all()
        return Response({"requests": [str(request) for request in requests]})
    
    def post(self, request):
        task_number = int(request.data.get('task_number'))
        number = int(request.data.get('number'))
        
        if task_number == 1:
            task1.delay(number)
            
        
        return Response({"success": f'Task with number {task_number} started'})