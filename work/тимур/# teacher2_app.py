# teacher_app.py
from flask import Flask, render_template_string, request, jsonify
import os
import webbrowser
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Исходные данные (имитация БД)
reports = [
    {"group": "221-111", "discipline": "Сети и телекоммуникации", "status": "отчёт составлен", "paper": "Отсутствует"},
    {"group": "221-111", "discipline": "Back-end разработка", "status": "На проверке", "paper": "Отсутствует"},
    {"group": "221-222", "discipline": "Сети и телекоммуникации", "status": "На доработке", "paper": "Отсутствует"},
    {"group": "221-222", "discipline": "Back-end разработка", "status": "Сдан", "paper": "Отсутствует"},
    {"group": "221-222", "discipline": "Сети и телекоммуникации", "status": "Сдан", "paper": "Отсутствует"},
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Преподаватель - Проверка отчётов</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 16px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 18px 20px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background-color: #f8f9fa;
            color: #333;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        tr:hover {
            background-color: #f8f9ff;
        }
        
        .status {
            font-weight: bold;
            padding: 6px 14px;
            border-radius: 20px;
            display: inline-block;
            font-size: 13px;
        }
        
        .status-composed {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffecb5;
        }
        
        .status-review {
            background-color: #cce5ff;
            color: #004085;
            border: 1px solid #b8daff;
        }
        
        .status-rework {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-done {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .btn-upload {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn-upload:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .upload-area {
            margin-top: 15px;
            padding: 15px;
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            text-align: center;
            background: #f7fafc;
            transition: all 0.3s;
        }
        
        .upload-area.drag-over {
            border-color: #667eea;
            background: #edf2ff;
        }
        
        .upload-input {
            display: none;
        }
        
        .upload-label {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #48bb78;
            color: white;
            padding: 8px 18px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .upload-label:hover {
            background: #38a169;
        }
        
        .file-status {
            font-size: 13px;
            margin-top: 10px;
            padding: 8px;
            border-radius: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .status-uploading {
            background-color: #e0f2fe;
            color: #0284c7;
        }
        
        .status-success {
            background-color: #dcfce7;
            color: #16a34a;
        }
        
        .status-error {
            background-color: #fee2e2;
            color: #dc2626;
        }
        
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #0284c7;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .action-cell {
            min-width: 280px;
        }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 12px 24px;
            border-radius: 10px;
            display: none;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .paper-absent {
            color: #e53e3e;
            font-weight: 500;
        }
        
        .progress-bar {
            width: 100%;
            height: 4px;
            background-color: #e2e8f0;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
        }
        
        @media (max-width: 768px) {
            body {
                padding: 20px;
            }
            th, td {
                padding: 12px;
                font-size: 14px;
            }
            .action-cell {
                min-width: 200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Проверка отчётов студентов</h1>
            <p>Загрузите отчёты на проверку | Drag & Drop файлы</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Группа</th>
                    <th>Дисциплина</th>
                    <th>Электронный отчёт</th>
                    <th>Бумажный отчёт</th>
                    <th>Действие</th>
                </tr>
            </thead>
            <tbody>
                {% for report in reports %}
                <tr data-group="{{ report.group }}" data-discipline="{{ report.discipline }}" data-status="{{ report.status }}">
                    <td style="font-weight: 500;">{{ report.group }}</td>
                    <td>{{ report.discipline }}</td>
                    <td>
                        <span class="status 
                            {% if report.status == 'отчёт составлен' %}status-composed
                            {% elif report.status == 'На проверке' %}status-review
                            {% elif report.status == 'На доработке' %}status-rework
                            {% elif report.status == 'Сдан' %}status-done
                            {% endif %}">
                            {{ report.status }}
                        </span>
                    </td>
                    <td>
                        <span class="paper-absent">📄 {{ report.paper }}</span>
                    </td>
                    <td class="action-cell">
                        {% if report.status == 'отчёт составлен' %}
                        <div class="upload-container" data-group="{{ report.group }}" data-discipline="{{ report.discipline }}">
                            <button class="btn-upload" onclick="showUploadForm('{{ report.group }}', '{{ report.discipline }}')">
                                📤 Загрузить на проверку
                            </button>
                            <div id="upload-form-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}" style="display: none;">
                                <div class="upload-area" id="drop-area-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}">
                                    <div>🐱‍💻 Перетащите файл сюда или</div>
                                    <label class="upload-label" for="file-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}">
                                        📁 Выберите файл
                                    </label>
                                    <input type="file" class="upload-input" id="file-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}" 
                                           data-group="{{ report.group }}" data-discipline="{{ report.discipline }}">
                                    <div class="file-status" id="status-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}"></div>
                                    <div class="progress-bar" id="progress-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}" style="display: none;">
                                        <div class="progress-fill" id="progress-fill-{{ report.group|replace('-', '') }}-{{ report.discipline|replace(' ', '') }}"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% else %}
                        <span style="color: #a0aec0; font-size: 13px;">🔒 Недоступно</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div id="toast" class="toast"></div>

    <script>
        function showUploadForm(group, discipline) {
            const formId = `upload-form-${group.replace(/-/g, '')}-${discipline.replace(/ /g, '')}`;
            const form = document.getElementById(formId);
            if (form.style.display === 'none' || !form.style.display) {
                form.style.display = 'block';
            } else {
                form.style.display = 'none';
            }
        }
        
        function showMessage(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.style.backgroundColor = isError ? '#e53e3e' : '#48bb78';
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
        
        function updateStatusUI(statusElement, progressBar, progressFill, statusType, message = '') {
            // Убираем все классы статуса
            statusElement.classList.remove('status-uploading', 'status-success', 'status-error');
            
            if (statusType === 'uploading') {
                statusElement.innerHTML = '<div class="spinner"></div> Файл загружается...';
                statusElement.classList.add('status-uploading');
                progressBar.style.display = 'block';
                // Анимируем прогресс бар
                let width = 0;
                const interval = setInterval(() => {
                    if (width < 90) {
                        width += 10;
                        progressFill.style.width = width + '%';
                    } else {
                        clearInterval(interval);
                    }
                }, 200);
                statusElement.progressInterval = interval;
            } else if (statusType === 'success') {
                if (statusElement.progressInterval) {
                    clearInterval(statusElement.progressInterval);
                }
                progressFill.style.width = '100%';
                setTimeout(() => {
                    progressBar.style.display = 'none';
                    progressFill.style.width = '0%';
                }, 500);
                statusElement.innerHTML = '✅ Успешно! Файл загружен';
                statusElement.classList.add('status-success');
            } else if (statusType === 'error') {
                if (statusElement.progressInterval) {
                    clearInterval(statusElement.progressInterval);
                }
                progressBar.style.display = 'none';
                progressFill.style.width = '0%';
                statusElement.innerHTML = `❌ Ошибка: ${message}`;
                statusElement.classList.add('status-error');
            }
        }
        
        async function uploadFile(file, group, discipline, rowElement, statusElement, progressBar, progressFill) {
            if (!file) {
                updateStatusUI(statusElement, progressBar, progressFill, 'error', 'Файл не выбран');
                return;
            }
            
            // Проверка типа файла
            const allowedTypes = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.txt', '.jpg', '.png'];
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(fileExt)) {
                updateStatusUI(statusElement, progressBar, progressFill, 'error', 'Неподдерживаемый тип файла');
                showMessage('Неподдерживаемый тип файла. Разрешены: PDF, DOC, DOCX, ZIP, RAR, TXT, JPG, PNG', true);
                return;
            }
            
            // Проверка размера файла (максимум 50MB)
            if (file.size > 50 * 1024 * 1024) {
                updateStatusUI(statusElement, progressBar, progressFill, 'error', 'Файл слишком большой (макс. 50MB)');
                showMessage('Файл превышает 50MB', true);
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('group', group);
            formData.append('discipline', discipline);
            
            // Показываем статус загрузки
            updateStatusUI(statusElement, progressBar, progressFill, 'uploading');
            
            try {
                const xhr = new XMLHttpRequest();
                
                // Отслеживаем прогресс загрузки
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        progressFill.style.width = percentComplete + '%';
                    }
                });
                
                const response = await new Promise((resolve, reject) => {
                    xhr.onload = () => resolve(xhr);
                    xhr.onerror = () => reject(new Error('Network error'));
                    xhr.open('POST', '/upload');
                    xhr.send(formData);
                });
                
                if (response.status === 200) {
                    const result = JSON.parse(response.responseText);
                    updateStatusUI(statusElement, progressBar, progressFill, 'success');
                    showMessage(result.message);
                    
                    // Обновляем статус в таблице
                    const statusSpan = rowElement.querySelector('td:nth-child(3) .status');
                    if (statusSpan) {
                        statusSpan.textContent = 'На проверке';
                        statusSpan.className = 'status status-review';
                    }
                    
                    // Обновляем кнопки
                    const uploadContainer = rowElement.querySelector('.upload-container');
                    if (uploadContainer) {
                        uploadContainer.innerHTML = `
                            <div style="background-color: #dcfce7; padding: 10px; border-radius: 8px; text-align: center;">
                                <div style="color: #16a34a; font-weight: 500;">✅ Отправлено на проверку</div>
                                <div style="font-size: 12px; color: #666; margin-top: 5px;">Файл: ${file.name}</div>
                            </div>
                        `;
                    }
                    
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    const error = JSON.parse(response.responseText);
                    updateStatusUI(statusElement, progressBar, progressFill, 'error', error.error || 'Ошибка загрузки');
                    showMessage(error.error || 'Ошибка загрузки', true);
                }
            } catch (error) {
                console.error('Upload error:', error);
                updateStatusUI(statusElement, progressBar, progressFill, 'error', 'Ошибка соединения с сервером');
                showMessage('Ошибка соединения с сервером', true);
            }
        }
        
        // Настройка drag-and-drop для всех областей
        document.querySelectorAll('.upload-area').forEach(area => {
            const input = area.querySelector('.upload-input');
            const group = input.getAttribute('data-group');
            const discipline = input.getAttribute('data-discipline');
            const statusElement = area.querySelector('.file-status');
            const progressBar = area.querySelector('.progress-bar');
            const progressFill = area.querySelector('.progress-fill');
            const rowElement = area.closest('tr');
            
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('drag-over');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('drag-over');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    uploadFile(files[0], group, discipline, rowElement, statusElement, progressBar, progressFill);
                }
            });
            
            input.addEventListener('change', (e) => {
                if (input.files.length > 0) {
                    uploadFile(input.files[0], group, discipline, rowElement, statusElement, progressBar, progressFill);
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, reports=reports)

@app.route('/upload', methods=['POST'])
def upload_file():
    group = request.form.get('group')
    discipline = request.form.get('discipline')
    
    if 'file' not in request.files:
        return jsonify({"error": "Файл не выбран"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400
    
    # Сохраняем файл
    filename = f"{group}_{discipline}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Если файл с таким именем существует, добавляем номер
    counter = 1
    while os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{name}_{counter}{ext}")
        counter += 1
    
    file.save(filepath)
    
    # Обновляем статус в "На проверке"
    for report in reports:
        if report['group'] == group and report['discipline'] == discipline:
            if report['status'] == 'отчёт составлен':
                report['status'] = "На проверке"
            break
    
    return jsonify({
        "message": f"Файл {file.filename} загружен, статус обновлён на 'На проверке'",
        "new_status": "На проверке",
        "filename": os.path.basename(filepath)
    })

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Открываем браузер автоматически
    threading.Timer(1.5, open_browser).start()
    print("🚀 Сервер запускается...")
    print("📁 Загруженные файлы будут сохраняться в папку 'uploads'")
    print("🌐 Браузер откроется автоматически через несколько секунд")
    print("⚠️ Для остановки сервера нажмите Ctrl+C")
    print("=" * 50)
    app.run(debug=True, use_reloader=False)