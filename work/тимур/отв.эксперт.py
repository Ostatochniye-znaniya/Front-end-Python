# -*- coding: utf-8 -*-

import json
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# HTML шаблон страницы
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Формирование зоны ответственности экспертов</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: white;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
        }

        .header {
            background: white;
            color: #333;
            padding: 30px;
            text-align: center;
            border-bottom: 2px solid #f0f0f0;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            color: #2c3e50;
        }

        .header p {
            font-size: 14px;
            color: #7f8c8d;
        }

        .content {
            padding: 30px;
        }

        .search-section {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }

        .search-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }

        .search-input:focus {
            outline: none;
            border-color: #3498db;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #3498db;
            color: white;
        }

        .btn-primary:hover {
            background: #2980b9;
        }

        .btn-secondary {
            background: #95a5a6;
            color: white;
        }

        .btn-secondary:hover {
            background: #7f8c8d;
        }

        .btn-success {
            background: #27ae60;
            color: white;
        }

        .btn-success:hover {
            background: #229954;
        }

        .btn-danger {
            background: #e74c3c;
            color: white;
        }

        .btn-danger:hover {
            background: #c0392b;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .table-container {
            overflow-x: auto;
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 1px solid #e0e0e0;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }

        tr:hover {
            background: #f8f9fa;
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
            border-radius: 8px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }

        .modal-header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
        }

        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }

        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        .required {
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Формирование зоны ответственности экспертов</h1>
            <p>Управление экспертами и их показателями</p>
        </div>

        <div class="content">
            <!-- Поиск -->
            <div class="search-section">
                <input type="text" id="searchInput" class="search-input" placeholder="Введите показатель, ФИО, или должность...">
                <button class="btn btn-primary" onclick="searchExperts()">Поиск</button>
            </div>

            <!-- Кнопки управления -->
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="openAccessModal()">Открыть доступ к редактированию</button>
                <button class="btn btn-secondary" onclick="openEditModal()">Редактировать данные</button>
                <button class="btn btn-success" id="addRowBtn">Добавить строку</button>
            </div>

            <!-- Таблица -->
            <div class="table-container">
                <table id="expertsTable">
                    <thead>
                        <tr>
                            <th>ФИО</th>
                            <th>Должность</th>
                            <th>Показатели</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <tr>
                            <td colspan="3" style="text-align: center; padding: 40px;">
                                Нет данных. Нажмите кнопку <strong>"Добавить строку"</strong> для создания записи
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>
        
    </div>

    <!-- Модальное окно для добавления нового эксперта -->
    <div id="addModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">Добавление нового эксперта</div>
            <div class="form-group">
                <label>ФИО эксперта: <span class="required">*</span></label>
                <input type="text" id="newFio" placeholder="Введите ФИО" autocomplete="off">
            </div>
            <div class="form-group">
                <label>Должность: <span class="required">*</span></label>
                <input type="text" id="newPosition" placeholder="Введите должность" autocomplete="off">
            </div>
            <div class="form-group">
                <label>Показатель: <span class="required">*</span></label>
                <textarea id="newIndicator" rows="3" placeholder="Введите показатель"></textarea>
            </div>
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="closeAddModal()">Отмена</button>
                <button class="btn btn-success" onclick="submitAdd()">Добавить</button>
            </div>
        </div>
    </div>

    <!-- Модальное окно для открытия доступа -->
    <div id="accessModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">Открыть доступ к редактированию</div>
            <div class="form-group">
                <label>Выберите экспертов:</label>
                <select id="accessExperts" multiple style="height: 150px;"></select>
                <small style="color: #666;">Удерживайте Ctrl для выбора нескольких</small>
            </div>
            <div class="form-group">
                <label>Комментарий:</label>
                <textarea id="accessComment" placeholder="Укажите причину открытия доступа..."></textarea>
            </div>
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="closeAccessModal()">Отмена</button>
                <button class="btn btn-success" onclick="submitAccess()">Подтвердить</button>
            </div>
        </div>
    </div>

    <!-- Модальное окно для редактирования данных эксперта -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">Редактирование данных эксперта</div>
            <div class="form-group">
                <label>Выберите эксперта:</label>
                <select id="editExpert" onchange="loadExpertData()"></select>
            </div>
            <div class="form-group">
                <label>ФИО эксперта:</label>
                <input type="text" id="editFio">
            </div>
            <div class="form-group">
                <label>Должность:</label>
                <input type="text" id="editPosition">
            </div>
            <div class="form-group">
                <label>Показатель:</label>
                <textarea id="editIndicator" rows="4"></textarea>
            </div>
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="closeEditModal()">Отмена</button>
                <button class="btn btn-danger" onclick="deleteExpert()">Удалить эксперта</button>
                <button class="btn btn-primary" onclick="submitEdit()">Сохранить изменения</button>
            </div>
        </div>
    </div>

    <script>
        let expertsData = [];
        let currentEditIndex = -1;

        // Загрузка данных из localStorage
        function loadData() {
            const savedData = localStorage.getItem('expertsData');
            if (savedData) {
                expertsData = JSON.parse(savedData);
            } else {
                expertsData = [];
            }
            renderTable(expertsData);
            updateSelects();
        }

        // Сохранение данных в localStorage
        function saveData() {
            localStorage.setItem('expertsData', JSON.stringify(expertsData));
        }

        // Отрисовка таблицы
        function renderTable(data) {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 40px;">Нет данных. Нажмите кнопку "Добавить строку" для создания записи</td></tr>';
                return;
            }
            
            data.forEach((expert) => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = expert.fio;
                row.insertCell(1).textContent = expert.position;
                row.insertCell(2).textContent = expert.indicator;
            });
        }

        // Открытие модального окна для добавления
        function openAddModal() {
            document.getElementById('newFio').value = '';
            document.getElementById('newPosition').value = '';
            document.getElementById('newIndicator').value = '';
            document.getElementById('addModal').style.display = 'flex';
        }

        // Закрытие модального окна добавления
        function closeAddModal() {
            document.getElementById('addModal').style.display = 'none';
        }

        // Добавление нового эксперта
        function submitAdd() {
            const fio = document.getElementById('newFio').value.trim();
            const position = document.getElementById('newPosition').value.trim();
            const indicator = document.getElementById('newIndicator').value.trim();
            
            if (!fio) {
                alert('Пожалуйста, введите ФИО эксперта');
                document.getElementById('newFio').focus();
                return;
            }
            
            if (!position) {
                alert('Пожалуйста, введите должность');
                document.getElementById('newPosition').focus();
                return;
            }
            
            if (!indicator) {
                alert('Пожалуйста, введите показатель');
                document.getElementById('newIndicator').focus();
                return;
            }
            
            const newExpert = {
                fio: fio,
                position: position,
                indicator: indicator
            };
            
            expertsData.push(newExpert);
            saveData();
            renderTable(expertsData);
            updateSelects();
            closeAddModal();
            
            alert('Эксперт успешно добавлен!');
        }

        // Поиск
        function searchExperts() {
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            
            if (!query) {
                renderTable(expertsData);
                return;
            }
            
            const filtered = expertsData.filter(expert => {
                return expert.fio.toLowerCase().includes(query) ||
                       expert.position.toLowerCase().includes(query) ||
                       expert.indicator.toLowerCase().includes(query);
            });
            
            renderTable(filtered);
            
            if (filtered.length === 0) {
                alert('По вашему запросу ничего не найдено');
            }
        }

        // Обновление выпадающих списков
        function updateSelects() {
            const accessSelect = document.getElementById('accessExperts');
            const editSelect = document.getElementById('editExpert');
            
            if (accessSelect) {
                accessSelect.innerHTML = '';
            }
            if (editSelect) {
                editSelect.innerHTML = '';
            }
            
            expertsData.forEach((expert, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = expert.fio;
                if (accessSelect) {
                    accessSelect.appendChild(option.cloneNode(true));
                }
                if (editSelect) {
                    editSelect.appendChild(option.cloneNode(true));
                }
            });
        }

        // Загрузка данных эксперта для редактирования
        function loadExpertData() {
            const index = parseInt(document.getElementById('editExpert').value);
            if (!isNaN(index) && expertsData[index]) {
                currentEditIndex = index;
                const expert = expertsData[index];
                document.getElementById('editFio').value = expert.fio;
                document.getElementById('editPosition').value = expert.position;
                document.getElementById('editIndicator').value = expert.indicator;
            }
        }

        // Удаление эксперта из модального окна
        function deleteExpert() {
            if (currentEditIndex >= 0 && currentEditIndex < expertsData.length) {
                if (confirm('Вы уверены, что хотите удалить этого эксперта?')) {
                    expertsData.splice(currentEditIndex, 1);
                    saveData();
                    renderTable(expertsData);
                    updateSelects();
                    closeEditModal();
                    alert('Эксперт удален');
                }
            }
        }

        // Модальные окна для доступа и редактирования
        function openAccessModal() {
            if (expertsData.length === 0) {
                alert('Нет данных. Сначала добавьте экспертов.');
                return;
            }
            document.getElementById('accessModal').style.display = 'flex';
        }

        function closeAccessModal() {
            document.getElementById('accessModal').style.display = 'none';
        }

        function openEditModal() {
            if (expertsData.length === 0) {
                alert('Нет данных для редактирования. Сначала добавьте экспертов.');
                return;
            }
            currentEditIndex = 0;
            document.getElementById('editExpert').value = "0";
            loadExpertData();
            document.getElementById('editModal').style.display = 'flex';
        }

        function closeEditModal() {
            document.getElementById('editModal').style.display = 'none';
            currentEditIndex = -1;
        }

        function submitAccess() {
            const selectedOptions = Array.from(document.getElementById('accessExperts').selectedOptions);
            const experts = selectedOptions.map(opt => expertsData[parseInt(opt.value)].fio);
            const comment = document.getElementById('accessComment').value;
            
            if (experts.length === 0) {
                alert('Пожалуйста, выберите хотя бы одного эксперта');
                return;
            }
            
            alert(`Доступ открыт для ${experts.length} экспертов:\n${experts.join(', ')}${comment ? '\\n\\nКомментарий: ' + comment : ''}`);
            closeAccessModal();
            document.getElementById('accessComment').value = '';
        }

        function submitEdit() {
            if (currentEditIndex < 0 || currentEditIndex >= expertsData.length) {
                alert('Ошибка: эксперт не найден');
                return;
            }
            
            const fio = document.getElementById('editFio').value.trim();
            const position = document.getElementById('editPosition').value.trim();
            const indicator = document.getElementById('editIndicator').value.trim();
            
            if (!fio) {
                alert('Пожалуйста, введите ФИО эксперта');
                return;
            }
            
            if (!position) {
                alert('Пожалуйста, введите должность');
                return;
            }
            
            if (!indicator) {
                alert('Пожалуйста, введите показатель');
                return;
            }
            
            expertsData[currentEditIndex] = { fio, position, indicator };
            saveData();
            renderTable(expertsData);
            updateSelects();
            
            alert(`Данные эксперта успешно обновлены!`);
            closeEditModal();
        }

        // Закрытие модальных окон по клику вне их
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }

        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            const addBtn = document.getElementById('addRowBtn');
            if (addBtn) {
                addBtn.onclick = function() {
                    openAddModal();
                };
            }
            loadData();
        });
        
        // Поиск по Enter
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchExperts();
                }
            });
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Подавляем вывод логов в консоль"""
        pass

def open_browser():
    """Открытие браузера через 2 секунды"""
    time.sleep(2)
    webbrowser.open('http://localhost:8080')

if __name__ == '__main__':
    print("=" * 60)
    print(" Запуск приложения 'Формирование зоны ответственности экспертов'")
    print("=" * 60)
    print(" Сервер запускается на http://localhost:8080")
    print(" Браузер откроется автоматически через 2 секунды")
    print(" Для остановки сервера нажмите Ctrl+C в терминале")
    print("=" * 60)
    print()
    print(" ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print(" 1. Нажмите кнопку 'Добавить строку'")
    print(" 2. В открывшемся окне введите:")
    print("    - ФИО эксперта")
    print("    - Должность")
    print("    - Показатель")
    print(" 3. Нажмите 'Добавить'")
    print(" 4. Для редактирования нажмите 'Редактировать данные'")
    print(" 5. Для удаления нажмите кнопку 'Удалить эксперта' в окне редактирования")
    print("=" * 60)
    
    # Запускаем браузер в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Запускаем сервер
    server = HTTPServer(('localhost', 8080), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n Остановка сервера...")
        server.server_close()
        print(" Сервер остановлен")