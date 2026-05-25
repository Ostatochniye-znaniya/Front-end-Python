# ОДИН ПОЛНЫЙ ФАЙЛ С ДОБАВЛЕННЫМИ ПОЛЯМИ - скопируйте и вставьте целиком

# ============= models.py - ДОБАВИТЬ ПОЛЯ В МОДЕЛЬ =============
"""
Добавьте эти поля в вашу модель InspectionAssignments (или Reports):

class InspectionAssignment(models.Model):
    # ... существующие поля ...
    electronic_review_remarks = models.TextField(blank=True, null=True, verbose_name="Электронные замечания по проверке")
    electronic_submitted = models.BooleanField(default=False, verbose_name="Электронная версия подана")
    
    # ИЛИ если в модели Reports:
    electronic_review_remarks = models.TextField(blank=True, null=True, verbose_name="Электронные замечания по проверке")
    electronic_submitted = models.BooleanField(default=False, verbose_name="Электронная версия подана")
"""

# ============= views.py - ПОЛНЫЙ КОД С НОВЫМИ ПОЛЯМИ =============
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.contrib import messages
import csv
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import json
from datetime import datetime

# Предполагаем, что у вас есть модель InspectionAssignment
# from .models import InspectionAssignment

def teacher_dashboard(request):
    """Страница преподавателя со списком назначенных проверок"""
    # Здесь получите ваши назначенные проверки из БД
    # Для демонстрации используем пример с новыми полями
    class FakeInspectionAssignment:
        def __init__(self, id, title, course, status, electronic_submitted=False, electronic_review_remarks=""):
            self.id = id
            self.title = title
            self.course = course
            self.status = status
            self.submission_count = 15
            self.electronic_submitted = electronic_submitted
            self.electronic_review_remarks = electronic_review_remarks
    
    assigned_checks = [
        FakeInspectionAssignment(1, "Лабораторная работа №1", "Программирование", "На проверке", True, "Все файлы загружены корректно"),
        FakeInspectionAssignment(2, "Курсовая работа", "Базы данных", "Проверено 50%", False, ""),
        FakeInspectionAssignment(3, "Тестирование", "Web-разработка", "Ожидает", True, "Требуется дополнительная проверка"),
    ]
    
    return render(request, 'teacher_dashboard.html', {
        'assigned_checks': assigned_checks,
        'teacher_name': "Иван Петрович",
    })

def edit_inspection(request, assignment_id):
    """Редактирование полей electronic_review_remarks и electronic_submitted"""
    # Получите объект из БД
    # inspection = get_object_or_404(InspectionAssignment, id=assignment_id)
    
    # Для демонстрации
    class FakeInspection:
        def __init__(self, id, title):
            self.id = id
            self.title = title
            self.electronic_submitted = False
            self.electronic_review_remarks = ""
    
    inspection = FakeInspection(assignment_id, f"Задание #{assignment_id}")
    
    if request.method == 'POST':
        # Обновление данных
        # inspection.electronic_submitted = request.POST.get('electronic_submitted') == 'on'
        # inspection.electronic_review_remarks = request.POST.get('electronic_review_remarks', '')
        # inspection.save()
        messages.success(request, 'Данные успешно сохранены!')
        return redirect('teacher_dashboard')
    
    return render(request, 'edit_inspection.html', {
        'inspection': inspection,
    })

def generate_report(request, assignment_id):
    """Генерация отчёта по заданию ВКЛЮЧАЯ НОВЫЕ ПОЛЯ"""
    # Здесь получите данные из БД с новыми полями
    assignment = {
        "id": assignment_id, 
        "title": f"Задание #{assignment_id}", 
        "course": "Курс",
        "electronic_submitted": True,
        "electronic_review_remarks": "Все документы проверены, замечаний нет"
    }
    
    submissions = [
        {
            "student_name": "Анна Смирнова", 
            "student_email": "anna@mail.ru", 
            "submitted_at": timezone.now(), 
            "grade": 85, 
            "teacher_comment": "Отлично!",
            "electronic_submitted": True,
            "electronic_review_remarks": "Работа принята"
        },
        {
            "student_name": "Иван Петров", 
            "student_email": "ivan@mail.ru", 
            "submitted_at": timezone.now(), 
            "grade": 45, 
            "teacher_comment": "Доработать",
            "electronic_submitted": False,
            "electronic_review_remarks": "Отсутствуют файлы"
        },
        {
            "student_name": "Мария Сидорова", 
            "student_email": "maria@mail.ru", 
            "submitted_at": timezone.now(), 
            "grade": None, 
            "teacher_comment": "",
            "electronic_submitted": True,
            "electronic_review_remarks": "Ожидает проверки"
        },
    ]
    
    report_format = request.GET.get('format', 'html')
    
    # HTML отчёт с новыми полями
    if report_format == 'html':
        return render(request, 'report.html', {
            'assignment': assignment,
            'submissions': submissions,
            'total_submissions': len(submissions),
            'avg_grade': sum(s['grade'] for s in submissions if s['grade']) / len([s for s in submissions if s['grade']]) if any(s['grade'] for s in submissions) else 0,
            'passed_count': len([s for s in submissions if s['grade'] and s['grade'] >= 60]),
            'failed_count': len([s for s in submissions if s['grade'] and s['grade'] < 60]),
            'electronic_submitted_count': len([s for s in submissions if s['electronic_submitted']]),
        })
    
    # CSV отчёт с новыми полями
    elif report_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="report_assignment_{assignment_id}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Студент', 'Email', 'Дата сдачи', 'Оценка', 'Статус', 
                        'Комментарий', 'Электронная подана', 'Электронные замечания'])
        for sub in submissions:
            writer.writerow([
                sub['student_name'], sub['student_email'],
                sub['submitted_at'].strftime('%Y-%m-%d %H:%M'),
                sub['grade'] if sub['grade'] else 'Не оценено',
                'Пройдено' if sub['grade'] and sub['grade'] >= 60 else 'Не пройдено' if sub['grade'] else 'На проверке',
                sub['teacher_comment'],
                'Да' if sub['electronic_submitted'] else 'Нет',
                sub['electronic_review_remarks']
            ])
        return response
    
    # PDF отчёт с новыми полями
    elif report_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="report_assignment_{assignment_id}.pdf"'
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Отчёт по заданию: {assignment['title']}")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Всего сдавших: {len(submissions)}")
        p.drawString(50, height - 100, f"Электронная версия подана: {assignment['electronic_submitted']}")
        
        # Замечания по проверке
        p.setFont("Helvetica", 10)
        text = p.beginText(50, height - 130)
        text.setFont("Helvetica", 10)
        text.textLine("Электронные замечания по проверке:")
        text.textLine(assignment['electronic_review_remarks'][:80])
        p.drawText(text)
        
        y = height - 180
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50, y, "Студент")
        p.drawString(180, y, "Оценка")
        p.drawString(250, y, "Электрон.")
        p.drawString(350, y, "Замечания")
        y -= 20
        
        p.setFont("Helvetica", 8)
        for sub in submissions:
            if y < 50:
                p.showPage()
                y = height - 50
                p.setFont("Helvetica-Bold", 9)
                p.drawString(50, y, "Студент")
                p.drawString(180, y, "Оценка")
                p.drawString(250, y, "Электрон.")
                p.drawString(350, y, "Замечания")
                y -= 20
                p.setFont("Helvetica", 8)
            
            p.drawString(50, y, sub['student_name'][:25])
            grade_str = str(sub['grade']) if sub['grade'] else "-"
            p.drawString(180, y, grade_str)
            p.drawString(250, y, "✓" if sub['electronic_submitted'] else "✗")
            p.drawString(350, y, sub['electronic_review_remarks'][:40])
            y -= 15
        
        p.save()
        response.write(buffer.getvalue())
        buffer.close()
        return response
    
    # JSON отчёт с новыми полями
    elif report_format == 'json':
        data = {
            'assignment_id': assignment_id,
            'assignment_title': assignment['title'],
            'electronic_submitted': assignment['electronic_submitted'],
            'electronic_review_remarks': assignment['electronic_review_remarks'],
            'statistics': {
                'total_submissions': len(submissions),
                'avg_grade': sum(s['grade'] for s in submissions if s['grade']) / len([s for s in submissions if s['grade']]) if any(s['grade'] for s in submissions) else 0,
                'electronic_submitted_count': len([s for s in submissions if s['electronic_submitted']]),
            },
            'submissions': [
                {
                    'student_name': s['student_name'],
                    'student_email': s['student_email'],
                    'submitted_at': s['submitted_at'].isoformat(),
                    'grade': s['grade'],
                    'status': 'passed' if s['grade'] and s['grade'] >= 60 else 'failed' if s['grade'] else 'pending',
                    'teacher_comment': s['teacher_comment'],
                    'electronic_submitted': s['electronic_submitted'],
                    'electronic_review_remarks': s['electronic_review_remarks']
                }
                for s in submissions
            ]
        }
        return HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), 
                          content_type='application/json; charset=utf-8')
    
    return HttpResponse("Неизвестный формат", status=400)


# ============= HTML ШАБЛОНЫ =============

# templates/teacher_dashboard.html - С КНОПКОЙ РЕДАКТИРОВАНИЯ НОВЫХ ПОЛЕЙ
TEACHER_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Панель преподавателя</title>
    <style>
        .assignment-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px;
            border-radius: 5px;
            background: #f9f9f9;
        }
        .btn {
            display: inline-block;
            padding: 8px 15px;
            margin: 5px;
            text-decoration: none;
            background: #007bff;
            color: white;
            border-radius: 3px;
        }
        .btn-edit {
            background: #28a745;
        }
        .btn-edit:hover { background: #218838; }
        .btn:hover { background: #0056b3; }
        .btn-group { margin-top: 10px; }
        .small-btn {
            background: #6c757d;
            font-size: 12px;
            padding: 5px 10px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }
        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: black; }
        .remarks {
            font-size: 14px;
            color: #666;
            margin-top: 8px;
            padding: 5px;
            background: #f0f0f0;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>Здравствуйте, {{ teacher_name }}</h1>
    <h2>Назначенные проверки</h2>
    
    {% for check in assigned_checks %}
    <div class="assignment-card">
        <h3>{{ check.title }}
            {% if check.electronic_submitted %}
                <span class="badge badge-success">✓ Электронная версия подана</span>
            {% else %}
                <span class="badge badge-warning">⚠ Электронная версия не подана</span>
            {% endif %}
        </h3>
        <p>Дисциплина: {{ check.course|default:"-" }}</p>
        <p>Статус: {{ check.status }}</p>
        
        {% if check.electronic_review_remarks %}
        <div class="remarks">
            <strong>📝 Электронные замечания:</strong> {{ check.electronic_review_remarks }}
        </div>
        {% endif %}
        
        <div class="btn-group">
            <a href="{% url 'generate_report' check.id %}" class="btn">
                📄 Составить отчёт
            </a>
            <a href="{% url 'edit_inspection' check.id %}" class="btn btn-edit">
                ✏️ Редактировать поля
            </a>
            <a href="{% url 'generate_report' check.id %}?format=csv" class="btn small-btn">
                📊 CSV
            </a>
            <a href="{% url 'generate_report' check.id %}?format=pdf" class="btn small-btn">
                📑 PDF
            </a>
            <a href="{% url 'generate_report' check.id %}?format=json" class="btn small-btn">
                🔧 JSON
            </a>
        </div>
    </div>
    {% empty %}
        <p>Нет назначенных проверок.</p>
    {% endfor %}
</body>
</html>
"""

# templates/edit_inspection.html - ФОРМА ДЛЯ РЕДАКТИРОВАНИЯ НОВЫХ ПОЛЕЙ
EDIT_INSPECTION_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Редактирование проверки</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        textarea {
            height: 100px;
        }
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
        }
        .btn {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn:hover {
            background: #0056b3;
        }
        .card {
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            max-width: 600px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Редактирование: {{ inspection.title }}</h2>
        
        <form method="POST">
            {% csrf_token %}
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="electronic_submitted" {% if inspection.electronic_submitted %}checked{% endif %}>
                    Электронная версия подана
                </label>
            </div>
            
            <div class="form-group">
                <label for="remarks">Электронные замечания по проверке:</label>
                <textarea id="remarks" name="electronic_review_remarks">{{ inspection.electronic_review_remarks }}</textarea>
            </div>
            
            <button type="submit" class="btn">Сохранить изменения</button>
            <a href="{% url 'teacher_dashboard' %}" style="margin-left: 10px;">Отмена</a>
        </form>
    </div>
</body>
</html>
"""

# templates/report.html - ОТЧЁТ С НОВЫМИ ПОЛЯМИ
REPORT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Отчёт: {{ assignment.title }}</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .passed { color: green; font-weight: bold; }
        .failed { color: red; }
        .stats { background: #e9ecef; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
        .btn { padding: 5px 10px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        .electronic-info {
            background: #d4edda;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }
        .badge-yes { background: #28a745; color: white; }
        .badge-no { background: #dc3545; color: white; }
    </style>
</head>
<body>
    <h1>Отчёт по заданию: {{ assignment.title }}</h1>
    
    <div class="electronic-info">
        <strong>📧 Информация об электронной подаче:</strong><br>
        Электронная версия подана: {% if assignment.electronic_submitted %}✅ Да{% else %}❌ Нет{% endif %}<br>
        Электронные замечания: {{ assignment.electronic_review_remarks|default:"Нет замечаний" }}
    </div>
    
    <div class="stats">
        <strong>Статистика:</strong><br>
        Всего сдало: {{ total_submissions }}<br>
        Средняя оценка: {{ avg_grade|floatformat:1 }}<br>
        Сдало (≥60): {{ passed_count }}<br>
        Не сдало: {{ failed_count }}<br>
        Электронную версию подали: {{ electronic_submitted_count }}
    </div>
    
    <a href="?format=csv" class="btn">Скачать CSV</a>
    <a href="?format=pdf" class="btn">Скачать PDF</a>
    <a href="?format=json" class="btn">Скачать JSON</a>
    <br><br>
    
    <table>
        <thead>
            <tr>
                <th>Студент</th>
                <th>Email</th>
                <th>Дата сдачи</th>
                <th>Оценка</th>
                <th>Статус</th>
                <th>Электронная подана</th>
                <th>Электронные замечания</th>
                <th>Комментарий</th>
            </tr>
        </thead>
        <tbody>
            {% for sub in submissions %}
            <tr>
                <td>{{ sub.student_name }}</td>
                <td>{{ sub.student_email }}</td>
                <td>{{ sub.submitted_at|date:"d.m.Y H:i" }}</td>
                <td>{{ sub.grade|default:"—" }}</td>
                <td class="{% if sub.grade and sub.grade >= 60 %}passed{% elif sub.grade %}failed{% endif %}">
                    {% if sub.grade >= 60 %}✓ Сдано{% elif sub.grade %}✗ Не сдано{% else %}⏳ На проверке{% endif %}
                </td>
                <td class="{% if sub.electronic_submitted %}passed{% endif %}">
                    {% if sub.electronic_submitted %}
                        <span class="badge badge-yes">✅ Да</span>
                    {% else %}
                        <span class="badge badge-no">❌ Нет</span>
                    {% endif %}
                </td>
                <td>{{ sub.electronic_review_remarks|default:"—" }}</td>
                <td>{{ sub.teacher_comment|default:"—" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


# ============= urls.py - ДОБАВЬТЕ ЭТИ МАРШРУТЫ =============
"""
from django.urls import path
from . import views

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/edit/<int:assignment_id>/', views.edit_inspection, name='edit_inspection'),
    path('teacher/report/<int:assignment_id>/', views.generate_report, name='generate_report'),
]
"""

# Установите библиотеку: pip install reportlab