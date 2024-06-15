from django.urls import path
from services import views

urlpatterns = [
    # Assessment CRUD
    path("assessmentlist", views.AssessmentList.as_view()),
    path("createassessment", views.CreateAssessment.as_view()),
    path("assessmentdetail/<str:pk>", views.AssessmentDetail.as_view()),
    # Experiment CRUD
    path("experimentlist", views.ExperimentList.as_view()),
    path("createexperiment", views.CreateExperiment.as_view()),
    path("experimentdetail/<str:pk>", views.ExperimentDetail.as_view()),
    # Deployment CRUD
    path("deploymentlist", views.DeploymentList.as_view()),
    path("createdeployment", views.CreateDeployment.as_view()),
    path("deploymentdetail/<str:pk>", views.DeploymentDetail.as_view()),
]
