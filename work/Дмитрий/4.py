# ОДИН ПОЛНЫЙ ФАЙЛ - РАЗБЛОКИРОВКА КНОПКИ ЗАГРУЗКИ ПОСЛЕ ЗАМЕЧАНИЙ
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
    ]
    
    title = models.CharField(max_length=200)
    course = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Поля для загрузки файлов
    original_file = models.FileField(upload_to='uploads/original/', blank=True, null=True)
    corrected_file = models.FileField(upload_to='uploads/corrected/', blank=True, null=True)
    corrected_file_uploaded_at = models.DateTimeField(blank=True, null=True)
    correction_attempts = models.IntegerField(default=0)
    
    # Поля для замечаний
    electronic_review_remarks = models.TextField(blank=True, null=True)
    electronic_submitted = models.BooleanField(default=False)
    lpr_rejection_reason = models.TextField(blank=True, null=True)
    lpr_comment = models.TextField(blank=True, null=True)
    lpr_name = models.CharField(max_length=100, blank=True, null=True)
    lpr_rejection_date = models.DateTimeField(blank=True, null=True)
"""

def teacher_dashboard(request):
    """Страница преподавателя со списком проверок"""
    class FakeInspectionAssignment:
        def __init__(self, id, title, course, status, electronic_submitted=False, 
                     electronic_review_remarks="", lpr_comment="", 
                     corrected_file_exists=False, correction_attempts=0):
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
            
            self.get_status_display = {
                'pending': 'На проверке',
                'approved': 'Одобрено',
                'rejected': 'Отклонён',
                'in_progress': 'В работе',
                'correction_required': 'Требуется исправление',
                'resubmitted': 'Повторно отправлено'
            }.get(status, status)
    
    assigned_checks = [
        FakeInspectionAssignment(1, "Лабораторная работа №1", "Программирование", "correction_required",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Найдены ошибки в коде",
                                 lpr_comment="Исправить оформление и добавить комментарии",
                                 corrected_file_exists=False,
                                 correction_attempts=1),
        
        FakeInspectionAssignment(2, "Курсовая работа", "Базы данных", "rejected",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Требуется доработка",
                                 lpr_comment="Нет пояснительной записки",
                                 corrected_file_exists=False,
                                 correction_attempts=0),
        
        FakeInspectionAssignment(3, "Тестирование", "Web-разработка", "approved",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Работа принята",
                                 lpr_comment="",
                                 corrected_file_exists=True,
                                 correction_attempts=2),
        
        FakeInspectionAssignment(4, "Дипломная работа", "ИС", "correction_required",
                                 electronic_submitted=False,
                                 electronic_review_remarks="Отсутствуют файлы",
                                 lpr_comment="Загрузите все файлы согласно требованиям",
                                 corrected_file_exists=False,
                                 correction_attempts=0),
        
        FakeInspectionAssignment(5, "Практика", "Python", "pending",
                                 electronic_submitted=True,
                                 electronic_review_remarks="Ожидает проверки",
                                 lpr_comment="",
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
                     correction_attempts, has_corrected_file):
            self.id = id
            self.title = title
            self.status = status
            self.lpr_comment = lpr_comment
            self.electronic_review_remarks = electronic_review_remarks
            self.correction_attempts = correction_attempts
            self.has_corrected_file = has_corrected_file
            self.correction_deadline = timezone.now() + timezone.timedelta(days=7)
    
    assignment = FakeAssignment(
        id=assignment_id,
        title=f"Задание #{assignment_id}",
        status="correction_required",
        lpr_comment="Исправьте ошибки в оформлении. Добавьте список литературы.",
        electronic_review_remarks="Найдены критические ошибки в коде",
        correction_attempts=1,
        has_corrected_file=False
    )
    
    return render(request, 'student_workspace.html', {
        'assignment': assignment,
        'student_name': "Анна Смирнова",
    })

def upload_corrected_file(request, assignment_id):
    """Обработка загрузки исправленной версии файла"""
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
        
        # Сохранение файла
        file_path = default_storage.save(f'uploads/corrected/assignment_{assignment_id}_{timezone.now().timestamp()}_{uploaded_file.name}', 
                                          ContentFile(uploaded_file.read()))
        
        # Здесь обновите БД:
        # assignment = InspectionAssignment.objects.get(id=assignment_id)
        # assignment.corrected_file = file_path
        # assignment.corrected_file_uploaded_at = timezone.now()
        # assignment.correction_attempts += 1
        # assignment.status = 'resubmitted'
        # assignment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Файл успешно загружен!',
            'file_name': uploaded_file.name,
            'file_size': f'{uploaded_file.size / 1024:.1f} KB',
            'attempts': 2  # Номер попытки
        })
    
    return JsonResponse({'success': False, 'error': 'Файл не выбран'})

def get_correction_status(request, assignment_id):
    """Получение статуса исправлений через AJAX"""
    # Здесь получите данные из БД
    status_data = {
        'status': 'correction_required',  # или 'resubmitted', 'approved'
        'can_upload': True,
        'last_file': None,
        'attempts': 1,
        'deadline': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
        'remarks': 'Исправьте ошибки в коде'
    }
    
    return JsonResponse(status_data)

def generate_report(request, assignment_id):
    """Генерация отчёта"""
    assignment = {
        "id": assignment_id,
        "title": f"Задание #{assignment_id}",
        "status": "correction_required",
        "correction_attempts": 2,
        "has_corrected_file": True,
        "corrected_file_name": "исправленная_версия_v2.pdf",
        "electronic_review_remarks": "После исправления работа стала лучше",
    }
    
    submissions = [
        {"student_name": "Анна Смирнова", "grade": 75, "correction_attempts": 2},
        {"student_name": "Иван Петров", "grade": 45, "correction_attempts": 1},
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
        writer.writerow(['Студент', 'Оценка', 'Попыток исправления', 'Файл загружен'])
        for sub in submissions:
            writer.writerow([sub['student_name'], sub['grade'], sub['correction_attempts'], 'Да' if assignment['has_corrected_file'] else 'Нет'])
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
        .status-correction_required { background: #ff9800; color: white; }
        .status-resubmitted { background: #2196f3; color: white; }
        .status-approved { background: #4caf50; color: white; }
        .status-rejected { background: #f44336; color: white; }
        
        .correction-info {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
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
                {% if check.status == 'correction_required' %}🔄 Требуется исправление
                {% elif check.status == 'resubmitted' %}📤 Повторно отправлено
                {% elif check.status == 'approved' %}✅ Одобрено
                {% elif check.status == 'rejected' %}❌ Отклонён
                {% else %}⏳ {{ check.get_status_display }}{% endif %}
            </span>
            
            {% if check.status == 'correction_required' %}
            <div class="correction-info">
                <strong>⚠️ Замечания ЛПР:</strong> {{ check.lpr_comment }}<br>
                <strong>📝 Электронные замечания:</strong> {{ check.electronic_review_remarks }}<br>
                <strong>🔄 Попыток исправления:</strong> {{ check.correction_attempts }}
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

# templates/student_workspace.html - СТРАНИЦА СТУДЕНТА С РАЗБЛОКИРОВАННОЙ КНОПКОЙ
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
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📝 {{ assignment.title }}</h1>
            <p>Студент: {{ student_name }}</p>
            
            {% if assignment.status == 'correction_required' %}
            <div class="remarks-box">
                <div class="remarks-title">⚠️ ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ</div>
                <p><strong>Замечания от ЛПР:</strong></p>
                <p>{{ assignment.lpr_comment }}</p>
                <p><strong>Электронные замечания:</strong> {{ assignment.electronic_review_remarks }}</p>
                <p><strong>Попытка исправления №</strong> <span id="attempt-number">{{ assignment.correction_attempts|add:"1" }}</span></p>
                <p><strong>Срок сдачи:</strong> <span class="deadline" id="deadline">{{ assignment.correction_deadline|date:"d.m.Y H:i" }}</span></p>
            </div>
            
            <!-- РАЗБЛОКИРОВАННАЯ КНОПКА ЗАГРУЗКИ -->
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
            
            <div id="message"></div>
            {% else %}
            <div class="alert alert-success">
                <strong>✅ Статус:</strong> {{ assignment.get_status_display }}<br>
                {% if assignment.has_corrected_file %}
                Исправленная версия уже загружена и находится на проверке.
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const uploadBtn = document.getElementById('upload-btn');
        const progressBar = document.getElementById('progress-bar');
        const progressFill = document.getElementById('progress-fill');
        const fileInfo = document.getElementById('file-info');
        const messageDiv = document.getElementById('message');
        let selectedFile = null;
        
        // Клик по области загрузки
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // Drag & Drop
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
        
        // Выбор файла
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
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
        
        // Загрузка файла
        uploadBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            
            const formData = new FormData();
            formData.append('corrected_file', selectedFile);
            
            uploadBtn.disabled = true;
            progressBar.style.display = 'block';
            progressFill.style.width = '0%';
            
            // Имитация прогресса
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
                            🔄 Попытка исправления №${result.attempts}
                        `;
                        showMessage(result.message, 'success');
                        uploadArea.style.display = 'none';
                        uploadBtn.style.display = 'none';
                        
                        // Обновляем номер попытки
                        const attemptSpan = document.getElementById('attempt-number');
                        if (attemptSpan) attemptSpan.textContent = result.attempts;
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
        
        // Проверка статуса каждые 30 секунд
        function checkStatus() {
            fetch(`/status/${ {{ assignment.id }} }/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'approved') {
                        location.reload();
                    }
                });
        }
        setInterval(checkStatus, 30000);
    </script>
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
    <title>Отчёт</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>Отчёт по заданию: {{ assignment.title }}</h1>
    <p>Статус: {{ assignment.status }}</p>
    <p>Попыток исправления: {{ assignment.correction_attempts }}</p>
    <table>
        <thead><tr><th>Студент</th><th>Оценка</th><th>Попыток</th></tr></thead>
        <tbody>
            {% for sub in submissions %}
            <tr><td>{{ sub.student_name }}</td><td>{{ sub.grade }}</td><td>{{ sub.correction_attempts }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


# ============= urls.py =============
"""
from django.urls import path
from . import views

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/workspace/<int:assignment_id>/', views.student_workspace, name='student_workspace'),
    path('upload/<int:assignment_id>/', views.upload_corrected_file, name='upload_corrected_file'),
    path('status/<int:assignment_id>/', views.get_correction_status, name='get_correction_status'),
    path('teacher/edit/<int:assignment_id>/', views.edit_inspection, name='edit_inspection'),
    path('teacher/report/<int:assignment_id>/', views.generate_report, name='generate_report'),
]
"""

