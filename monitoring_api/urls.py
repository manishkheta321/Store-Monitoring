from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import GenerateReportView, GetReportView

router = SimpleRouter()

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("trigger_report", GenerateReportView.as_view(), name="trigger-report"),
    path("get_report", GetReportView.as_view(), name="get-report"),
]
