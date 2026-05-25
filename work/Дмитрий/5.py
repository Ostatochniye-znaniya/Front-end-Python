# ОДИН ПОЛНЫЙ ФАЙЛ - ПОВТОРНАЯ ЗАГРУЗКА С ПЕРЕВОДОМ В СТАТУС "НА ПРОВЕРКЕ У ЛПР"
# Скопируйте и вставьте целиком

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import csv
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
import os
from datetime import datetime

# ============= models.py - ПОЛНАЯ МОДЕЛЬ =============
"""
class InspectionAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На проверке'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонён'),
        ('in_progress', 'В работе'),
        ('correction_required', 'Требуется исправление'),
        ('resubmitted', 'Повторно отправлено'),
        ('lpr_review', 'На проверке у ЛПР'),  # НОВЫЙ СТАТУС
        ('rework_needed', 'Нужна доработка'),
    ]
    
    title = models.CharField(max_length=200)
    course = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Поля для загрузки файлов
    original_file = models.FileField(upload_to='uploads/original/', blank=True, null=True)
    corrected_file = models.FileField(upload_to='uploads/corrected/', blank=True, null=True)
    corrected_file_uploaded_at = models.DateTimeField(blank=True, null=True)
    correction_attempts = models.IntegerField(default=0)
    
    # История версий
    previous_versions = models.TextField(blank=True, null=True)  # JSON с историей
    
    # Поля для замечаний
    electronic_review_remarks = models.TextField(blank=True, null=True)
    electronic_submitted = models.BooleanField(default=False)
    lpr_rejection_reason = models.TextField(blank=True, null=True)
    lpr_comment = models.TextField(blank=True, null=True)
    lpr_name = models.CharField(max_length=100, blank=True, null=True)
    lpr_rejection_date = models.DateTimeField(blank=True, null=True)
    
    # Дата последней отправки на проверку ЛПР
    last_submitted_to_lpr = models.DateTimeField(blank=True, null=True)
"""

def teacher_dashboard(request):
    """Страница преподавателя со списком проверок"""
    class FakeInspectionAssignment:
        def __init__(self, id, title, course, status, electronic_submitted=False, 
                     electronic_review_remarks="", lpr_comment="", 
                     corrected_file_exists=False, correction_attempts=0,
                     last_submitted_to_lpr=None):
            self.id = id
            self.title = title
            self.course = course
            self.status = status
            self.submission_count = 15
            self.electronic_submitted = electronic_submitted
            self.electronic_review_remarks = electronic_review_remarks
            self.lpr_comment = lpr_comment
            self.correction_attempts = correction_attempts
            self.has_corrected_file = corrected_file_exists
            self.last_submitted_to_lpr = last_submitted_to_lpr or timezone.now()
            
            self.get_status_display = {
                'pending': 'На проверке',
                'approved': 'Одобрено',
                'rejected': 'Отклонён',
                'in_progress': 'В работе',
                'correction_required': 'Требуется исправление',
                'resubmitted': 'Повторно отправлено',
                'lpr_review': 'На проверке у ЛПР',
                'rework_needed': 'Нужна доработка'
            }.get(status, status)
    
    assigned_checks = [
        FakeInspectionAssignment(1, "Лабораторная работа №1", "Программирование", "lpr_review",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Повторная проверка",
                                 lpr_comment="Ожидает решения ЛПР",
                                 corrected_file_exists=True,
                                 correction_attempts=2,
                                 last_submitted_to_lpr=timezone.now()),
        
        FakeInspectionAssignment(2, "Курсовая работа", "Базы данных", "rejected",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Требуется доработка",
                                 lpr_comment="Несоответствие требованиям",
                                 corrected_file_exists=False,
                                 correction_attempts=1),
        
        FakeInspectionAssignment(3, "Дипломная работа", "Информационные системы", "correction_required",
                                 electronic_submitted=False,
                                 electronic_review_remarks="Отсутствуют файлы",
                                 lpr_comment="Загрузите исправленную версию",
                                 corrected_file_exists=False,
                                 correction_attempts=0),
    ]
    
    return render(request, 'teacher_dashboard.html', {
        'assigned_checks': assigned_checks,
        'teacher_name': "Иван Петрович",
    })

def student_workspace(request, assignment_id):
    """Страница студента с возможностью загрузить исправленную версию"""
    class FakeAssignment:
        def __init__(self, id, title, status, lpr_comment, electronic_review_remarks, 
                     correction_attempts, has_corrected_file, last_submitted_to_lpr=None):
            self.id = id
            self.title = title
            self.status = status
            self.lpr_comment = lpr_comment
            self.electronic_review_remarks = electronic_review_remarks
            self.correction_attempts = correction_attempts
            self.has_corrected_file = has_corrected_file
            self.correction_deadline = timezone.now() + timezone.timedelta(days=7)
            self.last_submitted_to_lpr = last_submitted_to_lpr
    
    assignment = FakeAssignment(
        id=assignment_id,
        title=f"Задание #{assignment_id}",
        status="correction_required",
        lpr_comment="Исправьте ошибки в оформлении. Добавьте список литературы. После исправления работа будет отправлена на повторную проверку ЛПР.",
        electronic_review_remarks="Найдены критические ошибки в коде",
        correction_attempts=1,
        has_corrected_file=False,
        last_submitted_to_lpr=None
    )
    
    return render(request, 'student_workspace.html', {
        'assignment': assignment,
        'student_name': "Анна Смирнова",
    })

def upload_corrected_file(request, assignment_id):
    """Обработка загрузки исправленной версии файла с переводом в статус 'На проверке у ЛПР'"""
    if request.method == 'POST' and request.FILES.get('corrected_file'):
        uploaded_file = request.FILES['corrected_file']
        
        # Проверка расширения файла
        allowed_extensions = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.txt', '.py', '.java', '.cpp']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False, 
                'error': 'Неподдерживаемый формат файла. Разрешены: ' + ', '.join(allowed_extensions)
            })
        
        # Проверка размера (макс 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'Файл слишком большой. Максимум 50MB'})
        
        # Генерация имени файла с версией
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = default_storage.save(
            f'uploads/corrected/assignment_{assignment_id}/{version}_{uploaded_file.name}', 
            ContentFile(uploaded_file.read())
        )
        
        # Сохраняем предыдущую версию в историю (имитация)
        previous_versions = []
        
        # ОБНОВЛЕНИЕ БД:
        # assignment = InspectionAssignment.objects.get(id=assignment_id)
        # 
        # # Сохраняем предыдущую версию в историю
        # if assignment.corrected_file:
        #     history = json.loads(assignment.previous_versions or '[]')
        #     history.append({
        #         'file': assignment.corrected_file.name,
        #         'uploaded_at': assignment.corrected_file_uploaded_at.isoformat(),
        #         'attempt': assignment.correction_attempts
        #     })
        #     assignment.previous_versions = json.dumps(history)
        # 
        # # Обновляем файл и счётчик
        # assignment.corrected_file = file_path
        # assignment.corrected_file_uploaded_at = timezone.now()
        # assignment.correction_attempts += 1
        # 
        # # ГЛАВНОЕ: МЕНЯЕМ СТАТУС НА "НА ПРОВЕРКЕ У ЛПР"
        # assignment.status = 'lpr_review'
        # assignment.last_submitted_to_lpr = timezone.now()
        # 
        # # Добавляем запись в замечания о повторной отправке
        # new_remark = f"[{timezone.now().strftime('%d.%m.%Y %H:%M')}] Студент загрузил исправленную версию (попытка {assignment.correction_attempts}). Работа направлена на проверку ЛПР."
        # assignment.electronic_review_remarks = f"{assignment.electronic_review_remarks or ''}\n{new_remark}"
        # 
        # assignment.save()
        
        # Генерируем НОВЫЙ ОТЧЁТ для ЛПР
        report_generated = generate_lpr_report(assignment_id, correction_attempts=2)
        
        return JsonResponse({
            'success': True,
            'message': f'Файл успешно загружен! Работа отправлена на проверку ЛПР.',
            'file_name': uploaded_file.name,
            'file_size': f'{uploaded_file.size / 1024:.1f} KB',
            'attempts': 2,  # Номер попытки
            'new_status': 'lpr_review',
            'status_text': 'На проверке у ЛПР',
            'report_generated': report_generated,
            'submitted_at': timezone.now().strftime('%d.%m.%Y %H:%M')
        })
    
    return JsonResponse({'success': False, 'error': 'Файл не выбран'})

def generate_lpr_report(assignment_id, correction_attempts=1):
    """Генерация нового отчёта для ЛПР после повторной загрузки"""
    # Здесь логика генерации отчёта для ЛПР
    # Можно создать PDF или уведомление
    
    report_data = {
        'assignment_id': assignment_id,
        'correction_attempts': correction_attempts,
        'submitted_at': timezone.now().isoformat(),
        'status': 'sent_to_lpr'
    }
    
    # Имитация сохранения отчёта
    report_path = f'reports/lpr_report_{assignment_id}_{timezone.now().timestamp()}.json'
    
    return True

def lpr_dashboard(request):
    """Страница ЛПР со списком проверок на рассмотрении"""
    class FakeLprAssignment:
        def __init__(self, id, title, student_name, submitted_at, correction_attempts, 
                     electronic_review_remarks, corrected_file_exists):
            self.id = id
            self.title = title
            self.student_name = student_name
            self.submitted_at = submitted_at
            self.correction_attempts = correction_attempts
            self.electronic_review_remarks = electronic_review_remarks
            self.has_corrected_file = corrected_file_exists
    
    assignments_on_review = [
        FakeLprAssignment(1, "Лабораторная работа №1", "Анна Смирнова", 
                         timezone.now() - timezone.timedelta(hours=2), 2,
                         "Исправленная версия загружена 25.05.2024. Ожидает проверки ЛПР.", True),
        FakeLprAssignment(2, "Курсовая работа", "Иван Петров",
                         timezone.now() - timezone.timedelta(days=1), 1,
                         "Повторная отправка после доработки", True),
    ]
    
    return render(request, 'lpr_dashboard.html', {
        'assignments': assignments_on_review,
        'lpr_name': "Петрова М.И.",
    })

def lpr_review_action(request, assignment_id):
    """Действие ЛПР: одобрить или отклонить"""
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            # status = 'approved'
            message = 'Работа одобрена ЛПР'
        elif action == 'reject':
            # status = 'correction_required'
            message = 'Работа отправлена на доработку'
        else:
            return JsonResponse({'success': False, 'error': 'Неизвестное действие'})
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_status': 'approved' if action == 'approve' else 'correction_required'
        })
    
    return render(request, 'lpr_review.html', {'assignment_id': assignment_id})

def get_correction_status(request, assignment_id):
    """Получение статуса исправлений через AJAX"""
    status_data = {
        'status': 'lpr_review',  # или 'correction_required', 'approved'
        'status_text': 'На проверке у ЛПР',
        'can_upload': False,  # Пока на проверке у ЛПР - загружать нельзя
        'last_file': 'исправленная_версия_v2.pdf',
        'attempts': 2,
        'deadline': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
        'remarks': 'Работа направлена на проверку ЛПР. Ожидайте решения.',
        'submitted_to_lpr_at': timezone.now().strftime('%d.%m.%Y %H:%M')
    }
    
    return JsonResponse(status_data)

def generate_report(request, assignment_id):
    """Генерация полного отчёта с историей версий"""
    assignment = {
        "id": assignment_id,
        "title": f"Задание #{assignment_id}",
        "status": "lpr_review",
        "status_text": "На проверке у ЛПР",
        "correction_attempts": 2,
        "has_corrected_file": True,
        "corrected_file_name": "исправленная_версия_v2.pdf",
        "electronic_review_remarks": "[24.05.2024 15:30] Студент загрузил исправленную версию (попытка 2). Работа направлена на проверку ЛПР.",
        "last_submitted_to_lpr": timezone.now().strftime('%d.%m.%Y %H:%M'),
        "previous_versions": [
            {"file": "original_submission.pdf", "uploaded_at": "20.05.2024 10:00", "attempt": 0},
            {"file": "исправленная_версия_v1.pdf", "uploaded_at": "22.05.2024 14:30", "attempt": 1},
        ]
    }
    
    submissions = [
        {"student_name": "Анна Смирнова", "grade": None, "correction_attempts": 2, "status": "На проверке у ЛПР"},
        {"student_name": "Иван Петров", "grade": 45, "correction_attempts": 1, "status": "Требуется исправление"},
    ]
    
    report_format = request.GET.get('format', 'html')
    
    if report_format == 'html':
        return render(request, 'report.html', {
            'assignment': assignment,
            'submissions': submissions,
        })
    elif report_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="report_{assignment_id}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Студент', 'Статус', 'Попыток исправления', 'Дата отправки ЛПР', 'Замечания'])
        for sub in submissions:
            writer.writerow([
                sub['student_name'], 
                sub['status'], 
                sub['correction_attempts'],
                assignment['last_submitted_to_lpr'],
                assignment['electronic_review_remarks']
            ])
        return response
    elif report_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_{assignment_id}.pdf"'
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Отчёт по заданию: {assignment['title']}")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Статус: {assignment['status_text']}")
        p.drawString(50, height - 100, f"Попыток исправления: {assignment['correction_attempts']}")
        p.drawString(50, height - 120, f"Отправлено ЛПР: {assignment['last_submitted_to_lpr']}")
        
        p.setFont("Helvetica", 10)
        text = p.beginText(50, height - 150)
        text.textLine("Замечания и история:")
        text.textLine(assignment['electronic_review_remarks'][:100])
        p.drawText(text)
        
        p.save()
        response.write(buffer.getvalue())
        buffer.close()
        return response
    else:
        return render(request, 'report.html', {'assignment': assignment, 'submissions': submissions})

def edit_inspection(request, assignment_id):
    """Редактирование проверки"""
    return render(request, 'edit_inspection.html', {'inspection': {'id': assignment_id, 'title': f'Задание #{assignment_id}'}})


# ============= HTML ШАБЛОНЫ =============

# templates/teacher_dashboard.html
TEACHER_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Панель преподавателя</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #1a1a2e; margin-bottom: 20px; }
        
        .assignment-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-lpr_review { background: #9c27b0; color: white; }
        .status-correction_required { background: #ff9800; color: white; }
        .status-approved { background: #4caf50; color: white; }
        .status-rejected { background: #f44336; color: white; }
        
        .lpr-info {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 10px;
            margin: 10px 0;
        }
        
        .btn {
            display: inline-block;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 6px;
            margin: 5px;
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👨‍🏫 Панель преподавателя</h1>
        
        {% for check in assigned_checks %}
        <div class="assignment-card">
            <h3>{{ check.title }}</h3>
            <span class="status-badge status-{{ check.status }}">
                {% if check.status == 'lpr_review' %}🔄 На проверке у ЛПР
                {% elif check.status == 'correction_required' %}📝 Требуется исправление
                {% elif check.status == 'approved' %}✅ Одобрено
                {% elif check.status == 'rejected' %}❌ Отклонён
                {% else %}{{ check.get_status_display }}{% endif %}
            </span>
            
            {% if check.status == 'lpr_review' %}
            <div class="lpr-info">
                <strong>⚖️ На проверке у ЛПР</strong><br>
                Отправлено: {{ check.last_submitted_to_lpr|date:"d.m.Y H:i" }}<br>
                Попыток исправления: {{ check.correction_attempts }}
            </div>
            {% endif %}
            
            <div style="margin-top: 15px;">
                <a href="{% url 'generate_report' check.id %}" class="btn btn-primary">📄 Отчёт</a>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# templates/student_workspace.html - С ОБНОВЛЁННОЙ ЛОГИКОЙ
STUDENT_WORKSPACE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Загрузка исправленной версии</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        h1 { color: #1a1a2e; margin-bottom: 10px; }
        h2 { color: #16213e; font-size: 1.2em; margin: 20px 0 10px; }
        
        .remarks-box {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .lpr-info {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        .remarks-title {
            font-weight: bold;
            color: #e65100;
            margin-bottom: 10px;
        }
        
        .upload-area {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            transition: all 0.3s;
            cursor: pointer;
        }
        .upload-area.drag-over {
            background: #e3f2fd;
            border-color: #0056b3;
        }
        .upload-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        #file-input {
            display: none;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            margin: 10px 5px;
        }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,123,255,0.3);
        }
        .btn-primary:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .file-info {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            overflow: hidden;
            margin: 15px 0;
            display: none;
        }
        .progress-fill {
            height: 100%;
            background: #007bff;
            width: 0%;
            transition: width 0.3s;
        }
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .attempts-badge {
            background: #007bff;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            display: inline-block;
        }
        .deadline {
            color: #ff5722;
            font-weight: bold;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-lpr-review { background: #9c27b0; }
        .status-correction { background: #ff9800; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📝 {{ assignment.title }}</h1>
            <p>Студент: {{ student_name }}</p>
            
            <div id="status-container">
                <!-- Статус будет обновляться динамически -->
            </div>
            
            <div id="remarks-container">
                <div class="remarks-box">
                    <div class="remarks-title">⚠️ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ</div>
                    <p><strong>Замечания от ЛПР:</strong></p>
                    <p>{{ assignment.lpr_comment }}</p>
                    <p><strong>Электронные замечания:</strong> {{ assignment.electronic_review_remarks }}</p>
                    <p><strong>Попытка исправления №</strong> <span id="attempt-number">{{ assignment.correction_attempts|add:"1" }}</span></p>
                    <p><strong>Срок сдачи:</strong> <span class="deadline" id="deadline">{{ assignment.correction_deadline|date:"d.m.Y H:i" }}</span></p>
                </div>
            </div>
            
            <div id="lpr-info" class="lpr-info" style="display: none;">
                <strong>⚖️ Статус: На проверке у ЛПР</strong><br>
                <span id="lpr-status-text"></span><br>
                <span id="lpr-submitted-date"></span>
            </div>
            
            <!-- Блок загрузки файла -->
            <div id="upload-section">
                <h2>📤 Загрузить исправленную версию</h2>
                <div class="upload-area" id="upload-area">
                    <div class="upload-icon">📁</div>
                    <p>Перетащите файл сюда или <strong>нажмите для выбора</strong></p>
                    <p style="font-size: 12px; color: #666; margin-top: 10px;">
                        Поддерживаемые форматы: PDF, DOC, DOCX, ZIP, RAR, TXT, PY, JAVA, CPP (макс. 50MB)
                    </p>
                    <input type="file" id="file-input" accept=".pdf,.doc,.docx,.zip,.rar,.txt,.py,.java,.cpp">
                </div>
                
                <div class="progress-bar" id="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                
                <div id="file-info" class="file-info"></div>
                
                <div style="text-align: center;">
                    <button class="btn btn-primary" id="upload-btn" disabled>
                        📤 Загрузить исправленную версию
                    </button>
                </div>
            </div>
            
            <div id="message"></div>
        </div>
    </div>
    
    <script>
        let selectedFile = null;
        let currentStatus = '{{ assignment.status }}';
        
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const uploadBtn = document.getElementById('upload-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressFill = document.getElementById('progress-fill');
        const fileInfo = document.getElementById('file-info');
        const messageDiv = document.getElementById('message');
        const uploadSection = document.getElementById('upload-section');
        const remarksContainer = document.getElementById('remarks-container');
        const lprInfo = document.getElementById('lpr-info');
        
        // Проверка текущего статуса
        function checkAndUpdateStatus() {
            fetch(`/status/${ {{ assignment.id }} }/`)
                .then(res => res.json())
                .then(data => {
                    currentStatus = data.status;
                    
                    if (data.status === 'lpr_review') {
                        // Работа на проверке у ЛПР - скрываем форму загрузки
                        uploadSection.style.display = 'none';
                        remarksContainer.style.display = 'none';
                        lprInfo.style.display = 'block';
                        document.getElementById('lpr-status-text').innerHTML = `
                            <span class="status-indicator status-lpr-review"></span>
                            Работа направлена на проверку ЛПР ${data.submitted_to_lpr_at || ''}
                        `;
                        document.getElementById('lpr-submitted-date').innerHTML = `
                            <small>Ожидайте решения ЛПР. Вы будете уведомлены о результате.</small>
                        `;
                    } else if (data.status === 'correction_required') {
                        // Снова требуется исправление
                        uploadSection.style.display = 'block';
                        remarksContainer.style.display = 'block';
                        lprInfo.style.display = 'none';
                        if (data.remarks) {
                            const remarksBox = document.querySelector('.remarks-box');
                            if (remarksBox) {
                                const newRemark = document.createElement('p');
                                newRemark.innerHTML = `<strong>📌 Новые замечания:</strong> ${data.remarks}`;
                                remarksBox.appendChild(newRemark);
                            }
                        }
                    } else if (data.status === 'approved') {
                        uploadSection.style.display = 'none';
                        remarksContainer.style.display = 'none';
                        lprInfo.style.display = 'block';
                        lprInfo.style.borderLeftColor = '#4caf50';
                        document.getElementById('lpr-status-text').innerHTML = `
                            <span class="status-indicator" style="background: #4caf50;"></span>
                            ✅ РАБОТА ОДОБРЕНА ЛПР!
                        `;
                    }
                })
                .catch(err => console.error('Status check error:', err));
        }
        
        // Клик по области загрузки
        if (uploadArea) {
            uploadArea.addEventListener('click', () => fileInput.click());
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileSelect(files[0]);
                }
            });
        }
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });
        }
        
        function handleFileSelect(file) {
            const allowedExtensions = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.txt', '.py', '.java', '.cpp'];
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(ext)) {
                showMessage('Неподдерживаемый формат файла', 'error');
                uploadBtn.disabled = true;
                return;
            }
            
            if (file.size > 50 * 1024 * 1024) {
                showMessage('Файл слишком большой (макс. 50MB)', 'error');
                uploadBtn.disabled = true;
                return;
            }
            
            selectedFile = file;
            uploadBtn.disabled = false;
            showMessage(`Выбран файл: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`, 'success');
        }
        
        if (uploadBtn) {
            uploadBtn.addEventListener('click', async () => {
                if (!selectedFile) return;
                
                const formData = new FormData();
                formData.append('corrected_file', selectedFile);
                
                uploadBtn.disabled = true;
                progressBar.style.display = 'block';
                progressFill.style.width = '0%';
                
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 10;
                    if (progress <= 90) {
                        progressFill.style.width = progress + '%';
                    }
                }, 200);
                
                try {
                    const response = await fetch(`/upload/${ {{ assignment.id }} }/`, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                    
                    clearInterval(interval);
                    progressFill.style.width = '100%';
                    
                    const result = await response.json();
                    
                    setTimeout(() => {
                        if (result.success) {
                            fileInfo.style.display = 'block';
                            fileInfo.innerHTML = `
                                <strong>✅ Файл успешно загружен!</strong><br>
                                📄 ${result.file_name}<br>
                                📦 ${result.file_size}<br>
                                🔄 Попытка исправления №${result.attempts}<br>
                                <strong>📨 ${result.message}</strong><br>
                                <small>🕒 Отправлено: ${result.submitted_at}</small>
                            `;
                            showMessage(result.message, 'success');
                            
                            // Скрываем форму загрузки и показываем статус "На проверке у ЛПР"
                            setTimeout(() => {
                                uploadSection.style.display = 'none';
                                remarksContainer.style.display = 'none';
                                lprInfo.style.display = 'block';
                                document.getElementById('lpr-status-text').innerHTML = `
                                    <span class="status-indicator status-lpr-review"></span>
                                    ✅ Работа направлена на проверку ЛПР!
                                `;
                                document.getElementById('lpr-submitted-date').innerHTML = `
                                    <small>Отправлено: ${result.submitted_at}</small><br>
                                    <small>Ожидайте решения ЛПР.</small>
                                `;
                            }, 2000);
                        } else {
                            showMessage(result.error, 'error');
                            uploadBtn.disabled = false;
                        }
                        progressBar.style.display = 'none';
                    }, 500);
                    
                } catch (error) {
                    clearInterval(interval);
                    progressBar.style.display = 'none';
                    showMessage('Ошибка загрузки. Попробуйте ещё раз.', 'error');
                    uploadBtn.disabled = false;
                }
            });
        }
        
        function showMessage(msg, type) {
            messageDiv.innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
            setTimeout(() => {
                if (messageDiv.innerHTML.includes(msg)) {
                    messageDiv.innerHTML = '';
                }
            }, 5000);
        }
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        // Проверка статуса каждые 15 секунд
        setInterval(checkAndUpdateStatus, 15000);
        checkAndUpdateStatus();
    </script>
</body>
</html>
"""

# templates/lpr_dashboard.html - СТРАНИЦА ЛПР
LPR_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Панель ЛПР</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f3e5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #4a148c; margin-bottom: 20px; }
        
        .assignment-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .assignment-card:hover { transform: translateY(-2px); }
        
        .lpr-badge {
            display: inline-block;
            background: #9c27b0;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 11px;
            margin-left: 10px;
        }
        
        .btn {
            display: inline-block;
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        }
        .btn-approve { background: #28a745; color: white; }
        .btn-reject { background: #dc3545; color: white; }
        .btn-view { background: #007bff; color: white; }
        
        .remarks {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 14px;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            padding: 25px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
        }
        .modal textarea {
            width: 100%;
            height: 120px;
            margin: 15px 0;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚖️ Панель ЛПР</h1>
        <p>Здравствуйте, {{ lpr_name }}</p>
        <h3>📋 Работы на проверке ({{ assignments|length }})</h3>
        
        {% for assignment in assignments %}
        <div class="assignment-card" id="card-{{ assignment.id }}">
            <h3>{{ assignment.title }}
                <span class="lpr-badge">На проверке у ЛПР</span>
            </h3>
            <p><strong>Студент:</strong> {{ assignment.student_name }}</p>
            <p><strong>Дата отправки:</strong> {{ assignment.submitted_at|date:"d.m.Y H:i" }}</p>
            <p><strong>Попытка исправления:</strong> №{{ assignment.correction_attempts }}</p>
            
            <div class="remarks">
                <strong>📝 Замечания из предыдущей проверки:</strong><br>
                {{ assignment.electronic_review_remarks }}
            </div>
            
            <div>
                <button class="btn btn-view" onclick="viewFile({{ assignment.id }})">📄 Смотреть отчёт</button>
                <button class="btn btn-approve" onclick="showModal({{ assignment.id }}, 'approve')">✅ Одобрить</button>
                <button class="btn btn-reject" onclick="showModal({{ assignment.id }}, 'reject')">❌ Отклонить</button>
            </div>
        </div>
        {% empty %}
            <p>Нет работ на проверке</p>
        {% endfor %}
    </div>
    
    <!-- Модальное окно для комментария -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <h3 id="modal-title">Комментарий ЛПР</h3>
            <textarea id="comment" placeholder="Введите ваше решение и замечания..."></textarea>
            <button class="btn btn-approve" onclick="submitDecision()">Подтвердить</button>
            <button class="btn btn-view" onclick="closeModal()">Отмена</button>
        </div>
    </div>
    
    <script>
        let currentAssignmentId = null;
        let currentAction = null;
        
        function viewFile(assignmentId) {
            window.open(`/teacher/report/${assignmentId}/`, '_blank');
        }
        
        function showModal(assignmentId, action) {
            currentAssignmentId = assignmentId;
            currentAction = action;
            const modal = document.getElementById('modal');
            const title = document.getElementById('modal-title');
            
            if (action === 'approve') {
                title.innerHTML = '✅ Подтверждение одобрения';
                document.getElementById('comment').placeholder = 'Введите комментарий к одобрению (необязательно)...';
            } else {
                title.innerHTML = '❌ Отклонение работы';
                document.getElementById('comment').placeholder = 'Укажите причину отклонения и что нужно исправить...';
            }
            modal.style.display = 'flex';
        }
        
        function closeModal() {
            document.getElementById('modal').style.display = 'none';
            document.getElementById('comment').value = '';
        }
        
        function submitDecision() {
            const comment = document.getElementById('comment').value;
            
            fetch(`/lpr/review/${currentAssignmentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `action=${currentAction}&comment=${encodeURIComponent(comment)}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    const card = document.getElementById(`card-${currentAssignmentId}`);
                    if (card) card.remove();
                    closeModal();
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(err => {
                alert('Ошибка при отправке решения');
            });
        }
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    </script>
</body>
</html>
"""

LPR_REVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Рассмотрение работы</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .card { max-width: 600px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Рассмотрение работы №{{ assignment_id }}</h2>
        <form method="POST">
            {% csrf_token %}
            <select name="action">
                <option value="approve">Одобрить</option>
                <option value="reject">Отклонить</option>
            </select>
            <textarea name="comment" placeholder="Комментарий ЛПР"></textarea>
            <button type="submit">Отправить</button>
        </form>
    </div>
</body>
</html>
"""

EDIT_INSPECTION_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Редактирование проверки</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .card { max-width: 500px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        textarea { width: 100%; height: 100px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Редактирование: {{ inspection.title }}</h2>
        <form method="POST">
            {% csrf_token %}
            <div class="form-group">
                <label>Электронные замечания:</label>
                <textarea name="remarks">{{ inspection.electronic_review_remarks }}</textarea>
            </div>
            <button type="submit" class="btn">Сохранить</button>
        </form>
    </div>
</body>
</html>
"""

REPORT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Отчёт по проверке</title>
    <style>
        body { font-family: 'Segoe UI', Arial; margin: 20px; background: white; }
        h1 { color: #1a1a2e; }
        .status-lpr { background: #f3e5f5; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #9c27b0; }
        .version-history { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #007bff; color: white; }
        .btn { padding: 8px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px; }
    </style>
</head>
<body>
    <h1>📊 Отчёт по заданию: {{ assignment.title }}</h1>
    
    <div class="status-lpr">
        <strong>⚖️ Статус: {{ assignment.status_text }}</strong><br>
        Отправлено на проверку ЛПР: {{ assignment.last_submitted_to_lpr }}<br>
        Попыток исправления: {{ assignment.correction_attempts }}
    </div>
    
    {% if assignment.previous_versions %}
    <div class="version-history">
        <strong>📚 История версий:</strong><br>
        {% for version in assignment.previous_versions %}
        - {{ version.uploaded_at }}: {{ version.file }} (попытка {{ version.attempt }})<br>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="remarks">
        <strong>📝 Замечания и комментарии:</strong><br>
        {{ assignment.electronic_review_remarks|linebreaksbr }}
    </div>
    
    <div style="margin: 20px 0;">
        <a href="?format=csv" class="btn">📥 CSV</a>
        <a href="?format=pdf" class="btn">📥 PDF</a>
    </div>
    
    <table>
        <thead>
            <tr><th>Студент</th><th>Статус</th><th>Попыток исправления</th><th>Замечания</th></tr>
        </thead>
        <tbody>
            {% for sub in submissions %}
            <tr>
                <td>{{ sub.student_name }}</td>
                <td>{{ sub.status }}</td>
                <td>{{ sub.correction_attempts }}</td>
                <td>{{ sub.grade|default:"—" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


# ============= urls.py - ПОЛНЫЕ МАРШРУТЫ =============
"""
from django.urls import path
from . import views

urlpatterns = [
    # Преподаватель
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/edit/<int:assignment_id>/', views.edit_inspection, name='edit_inspection'),
    path('teacher/report/<int:assignment_id>/', views.generate_report, name='generate_report'),
    
    # Студент
    path('student/workspace/<int:assignment_id>/', views.student_workspace, name='student_workspace'),
    path('upload/<int:assignment_id>/', views.upload_corrected_file, name='upload_corrected_file'),
    path('status/<int:assignment_id>/', views.get_correction_status, name='get_correction_status'),
    
    # ЛПР
    path('lpr/dashboard/', views.lpr_dashboard, name='lpr_dashboard'),
    path('lpr/review/<int:assignment_id>/', views.lpr_review_action, name='lpr_review_action'),
]
"""
