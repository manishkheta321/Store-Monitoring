from uuid import uuid4

from django.http import HttpResponse, JsonResponse
from rest_framework import views
from rest_framework.decorators import action

from .models import Report, ReportStatus
from .serializers import ReportSerializer
from .services import trigger_report_generation


class GenerateReportView(views.APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        # Generate a unique report_id (you might use a UUID library for this)
        report_id = uuid4()

        # Store the report_id and initial status in the reports table
        new_report = Report(id=report_id, status=ReportStatus.RUNNING)
        new_report.save()

        # Asynchronously start the report generation process
        # This could involve running a task in a separate thread or using a task queue (e.g., Celery)
        # For simplicity, we are calling the generate_report function directly
        trigger_report_generation(report_id=report_id)
        return JsonResponse({"report_id": report_id})


class GetReportView(views.APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        report_id = request.GET.get("report_id")

        # Retrieve the report status from the reports table
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return JsonResponse({"error": "Invalid report_id"})

        # If the report is still running, return 'Running'
        if report.status == ReportStatus.RUNNING:
            return JsonResponse({"status": ReportStatus.RUNNING})

        # If the report is complete, get the CSV file and return 'Complete'
        file_path = f"data/{report.id}.csv"
        with open(file_path, "r") as file:
            response = HttpResponse(file.read(), content_type="text/csv")
            response[
                "Content-Disposition"
            ] = f"attachment; filename={report_id}_report.csv"
            return response
