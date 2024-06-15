from django.urls import path, include
from project import views, router_urls

urlpatterns = [

    #  Project CRUD
    path("projectlist", views.ProjectList.as_view()),
    path("licenselist", views.LicenseList.as_view()),
    path("createproject", views.CreateProject.as_view()),

    path("projectlist/", views.ProjectList.as_view()),
    path("licenselist/", views.LicenseList.as_view()),
    path("createproject/", views.CreateProject.as_view()),
    
    path("projectdetail/<str:pk>", views.ProjectDetail.as_view()),
    path("licensedetail/<str:pk>", views.LicenseDetail.as_view()),

    # User Allocation
    path("licenseinformation", views.LicenseInformation.as_view()),
    path("customerusers", views.CustomerUsers.as_view()),
    path("userallocation/<str:pk>", views.UserAllocation.as_view()),

    # User View
    path("coursecatalog", views.CourseCatalog.as_view()),
    path("registeredcourses", views.RegisteredCourses.as_view()),
    path("registeredapprenticeships/", views.RegisteredApprenticeships.as_view()),
    path("registeredassessments/", views.RegisteredAssessments.as_view()),
    path("registeredassessments/<str:pk>/", views.RegisteredAssessments.as_view()),
    path("userviewprojects/<str:pk>", views.UserViewProjects.as_view()),

    # Reports
    path("customersreport", views.CustomersReport.as_view()),
    path("adminsreport", views.AdminsReport.as_view()),
    path("projectsreport", views.ProjectsReport.as_view()),
    path("usersreport", views.UsersReport.as_view()),
    path("userdetailreport", views.UserDetailReport.as_view()),

    path("customersreport/", views.CustomersReport.as_view()),
    path("adminsreport/", views.AdminsReport.as_view()),
    path("projectsreport/", views.ProjectsReport.as_view()),
    path("usersreport/", views.UsersReport.as_view()),
    path("userdetailreport/", views.UserDetailReport.as_view()),

    # Download Reports
    path("downloadreport/<str:pk>", views.DownloadReport.as_view()),
    path("userdetailedcsv/<str:pk>", views.UserDetailedCSV.as_view()),
    # path("projectdownloadreport/", views.ProjectUserDetailedCSV.as_view()),
    path("projectuserdetailedcsv/", views.ProjectUserDetailedCSV.as_view()),
    path(r'v2/', include(router_urls.router.urls)),
]
