from rest_framework.routers import DefaultRouter
from .viewsets import (ProjectViewset, GCIndexReportViewset, GCIndexAssessmentViewset)
from django.urls import path, include
router = DefaultRouter()

router.register(r'project', ProjectViewset, basename='project',)
router.register(r'gcindex', GCIndexAssessmentViewset, basename='gcindex',)
router.register(r'gcindex_report', GCIndexReportViewset, basename='gcindex_report',)
urlpatterns = router.urls