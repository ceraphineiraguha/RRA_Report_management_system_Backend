# report/urls.py
from django.urls import path
from .views import (
    ReportCreateView,
    ReportUpdateView,
    ReportDeleteView,
    ReportListView,
    ReportByLevelView,
    ReportByIdView,
    ReportByTitleView,
    ReportByUserView,
    ReportCountView,
    ReportTrendView,
    ReportDownloadPDFView,
    ReportDownloadExcelView,
    ReportDownloadAllPDFView,
    ReportDownloadAllExcelView,
    ReportsByCreatorView,
    ReportsBySubordinatesView,
    ReportApproveView  # New
)

urlpatterns = [
    path('create/', ReportCreateView.as_view(), name='report-create'),
    path('update/<int:pk>/', ReportUpdateView.as_view(), name='report-update'),
    path('delete/<int:pk>/', ReportDeleteView.as_view(), name='report-delete'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('by_level/<str:level>/', ReportByLevelView.as_view(), name='report-by-level'),
    path('report/<int:pk>/', ReportByIdView.as_view(), name='report-detail'),
    path('by_title/<str:title>/', ReportByTitleView.as_view(), name='report-by-title'),
    path('by_user/<str:user>/', ReportByUserView.as_view(), name='report-by-user'),
    path('count/', ReportCountView.as_view(), name='report-count'),
    path('trend/', ReportTrendView.as_view(), name='report-trend'),
    path('download/pdf/<int:pk>/', ReportDownloadPDFView.as_view(), name='report-download-pdf'),
    path('download/excel/<int:pk>/', ReportDownloadExcelView.as_view(), name='report-download-excel'),
    path('download/all/pdf/', ReportDownloadAllPDFView.as_view(), name='report-download-all-pdf'),
    path('download/all/excel/', ReportDownloadAllExcelView.as_view(), name='report-download-all-excel'),
    path('reports/by_creator/<int:user_id>/', ReportsByCreatorView.as_view(), name='reports-by-creator'),
    path('reports/by_subordinates/<int:creator_id>/', ReportsBySubordinatesView.as_view(), name='reports-by-subordinates'),
    path('approve/<int:pk>/', ReportApproveView.as_view(), name='report-approve'),  # New
]
