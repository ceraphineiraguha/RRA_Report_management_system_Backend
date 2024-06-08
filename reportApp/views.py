from io import BytesIO
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Report
from .serializers import ReportSerializer
from userApp.models import CustomUser  # Assuming your CustomUser model is in a users app

import logging

# report/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Report
from .serializers import ReportSerializer
from userApp.models import CustomUser

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')

        # Retrieve the logged-in user
        user = request.user

        # Determine the level based on the user's role
        if user.role == 'unit user':
            level = 'unit'
        elif user.role == 'head of department':
            level = 'department'
        elif user.role == 'head of division':
            level = 'division'
        else:
            level = 'user'

        # Create the report with the determined level and logged-in user as creator
        report = Report.objects.create(
            title=title,
            description=description,
            level=level,
            user=user  # Correct field name
        )

        # Serialize the report and return the response
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReportUpdateView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

class ReportDeleteView(generics.DestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

class ReportByLevelView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        level = self.kwargs['level']
        return Report.objects.filter(level=level)

class ReportByIdView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

class ReportByTitleView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        title = self.kwargs['title']
        return Report.objects.filter(title__icontains=title)

class ReportByUserView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.kwargs['user']
        return Report.objects.filter(user__username=user) | \
               Report.objects.filter(user__email=user) | \
               Report.objects.filter(user__phone=user)

class ReportCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Report.objects.count()
        return Response({"count": count}, status=status.HTTP_200_OK)

class ReportTrendView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_trend(self, interval):
        end_date = timezone.now()
        start_date = end_date - interval
        return Report.objects.filter(created_date__range=(start_date, end_date)).count()

    def get(self, request):
        trends = {
            "daily": self.get_trend(timedelta(days=1)),
            "weekly": self.get_trend(timedelta(weeks=1)),
            "monthly": self.get_trend(timedelta(days=30)),
            "three_months": self.get_trend(timedelta(days=30*3)),
            "six_months": self.get_trend(timedelta(days=30*6)),
            "yearly": self.get_trend(timedelta(days=365)),
            "three_years": self.get_trend(timedelta(days=365*3)),
            "five_years": self.get_trend(timedelta(days=365*5)),
            "ten_years": self.get_trend(timedelta(days=365*10))
        }
        return Response(trends, status=status.HTTP_200_OK)



from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


class ReportDownloadPDFView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        report = Report.objects.get(pk=pk)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'

        # Generate PDF content
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        data = [
            ["ID", "User", "Level", "Title", "Description", "Created Date"],
            [report.id, report.user.username, report.level, report.title, report.description, report.created_date]
        ]
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)
        return response


class ReportDownloadExcelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        report = Report.objects.get(pk=pk)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="report_{pk}.xls"'

        # Generate Excel content
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        # Headers
        headers = ["ID", "User", "Level", "Title", "Description", "Created Date"]
        ws.append(headers)

        # Data
        data = [report.id, report.user.username, report.level, report.title, report.description, report.created_date]
        ws.append(data)

        # Set column width and alignment
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width
            for cell in col:
                cell.alignment = Alignment(horizontal='center', vertical='center')

        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        excel_data = buffer.getvalue()
        buffer.close()

        response.write(excel_data)
        return response



class ReportDownloadAllPDFView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.all()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="all_reports.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add table headers
        headers = ["ID", "User", "Level", "Title", "Description", "Created Date"]
        data = [headers]

        # Add report data
        for report in reports:
            row = [report.id, report.user.username, report.level, report.title, report.description, report.created_date]
            data.append(row)

        # Generate PDF table
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)
        return response


class ReportDownloadAllExcelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.all()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="all_reports.xls"'

        wb = Workbook()
        ws = wb.active
        ws.title = "All Reports"

        # Add headers
        headers = ["ID", "User", "Level", "Title", "Description", "Created Date"]
        ws.append(headers)

        # Add report data
        for report in reports:
            row = [report.id, report.user.username, report.level, report.title, report.description, report.created_date]
            ws.append(row)

        # Set column width and alignment
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width
            for cell in col:
                cell.alignment = Alignment(horizontal='center', vertical='center')

        buffer = BytesIO()
        wb.save(buffer)
        excel_data = buffer.getvalue()
        buffer.close()

        response.write(excel_data)
        return response
