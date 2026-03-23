from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-2024-university'

# Конфигурация базы данных (укажите свои данные)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'knowledge_test_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Получение соединения с базой данных"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Ошибка подключения: {e}")
        return None

# Инициализация необходимых таблиц
def init_tables():
    """Создание дополнительных таблиц если их нет"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Таблица периодов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            is_current BOOLEAN DEFAULT FALSE,
            start_date DATE,
            end_date DATE
        )
    """)
    
    # Таблица выбранных дисциплин для групп
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_disciplines (
            id INT PRIMARY KEY AUTO_INCREMENT,
            group_id INT NOT NULL,
            discipline_id INT NOT NULL,
            period_id INT NOT NULL,
            is_selected BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE CASCADE,
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE,
            FOREIGN KEY (period_id) REFERENCES periods(id) ON DELETE CASCADE,
            UNIQUE KEY unique_group_discipline_period (group_id, discipline_id, period_id)
        )
    """)
    
    # Добавляем текущий период если нет
    cursor.execute("SELECT COUNT(*) FROM periods WHERE is_current = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO periods (name, is_current, start_date, end_date)
            VALUES ('Весенний семестр 2024', 1, '2024-02-01', '2024-06-30')
        """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Запускаем инициализацию таблиц
init_tables()

@app.route('/')
def index():
    """Главная страница"""
    user_data = {
        'name': 'Иванов Иван Иванович',
        'role': 'Заведующий кафедрой',
        'department_id': 1
    }
    session['user'] = user_data
    
    # Получаем список факультетов
    conn = get_db_connection()
    faculties = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM faculties ORDER BY name")
        faculties = cursor.fetchall()
        cursor.close()
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, user=user_data, faculties=faculties)

@app.route('/api/departments')
def get_departments():
    """Получить кафедры"""
    faculty_id = request.args.get('faculty_id', type=int)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if faculty_id:
        cursor.execute("""
            SELECT id, name, faculty_id 
            FROM departments 
            WHERE faculty_id = %s 
            ORDER BY name
        """, (faculty_id,))
    else:
        cursor.execute("SELECT id, name, faculty_id FROM departments ORDER BY name")
    
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(departments)

@app.route('/api/groups')
def get_groups():
    """Получить группы с фильтрацией"""
    department_id = request.args.get('department_id', type=int)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            sg.id,
            sg.name as group_name,
            d.id as department_id,
            d.name as department_name,
            f.id as faculty_id,
            f.name as faculty_name
        FROM study_groups sg
        JOIN departments d ON sg.department_id = d.id
        JOIN faculties f ON d.faculty_id = f.id
    """
    
    if department_id:
        query += " WHERE sg.department_id = %s"
        cursor.execute(query, (department_id,))
    else:
        cursor.execute(query)
    
    groups = cursor.fetchall()
    
    result = []
    for group in groups:
        result.append({
            'id': group['id'],
            'name': group['group_name'],
            'department_id': group['department_id'],
            'department_name': group['department_name'],
            'faculty_id': group['faculty_id'],
            'faculty_name': group['faculty_name']
        })
    
    cursor.close()
    conn.close()
    
    return jsonify(result)

@app.route('/api/groups/<int:group_id>/disciplines')
def get_group_disciplines(group_id):
    """Получить дисциплины для группы"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            d.id,
            d.name as discipline_name,
            dep.name as department_name,
            COALESCE(gd.is_selected, 0) as is_selected
        FROM disciplines d
        JOIN departments dep ON d.department_id = dep.id
        LEFT JOIN group_disciplines gd ON d.id = gd.discipline_id 
            AND gd.group_id = %s 
            AND gd.period_id = (SELECT id FROM periods WHERE is_current = 1 LIMIT 1)
        WHERE d.department_id = (SELECT department_id FROM study_groups WHERE id = %s)
        ORDER BY d.name
    """
    
    cursor.execute(query, (group_id, group_id))
    disciplines = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(disciplines)

@app.route('/api/groups/<int:group_id>/selected-disciplines')
def get_selected_disciplines(group_id):
    """Получить выбранные дисциплины для группы"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            d.id,
            d.name as discipline_name,
            dep.name as department_name
        FROM group_disciplines gd
        JOIN disciplines d ON gd.discipline_id = d.id
        JOIN departments dep ON d.department_id = dep.id
        WHERE gd.group_id = %s 
            AND gd.period_id = (SELECT id FROM periods WHERE is_current = 1 LIMIT 1)
            AND gd.is_selected = 1
        ORDER BY d.name
    """
    
    cursor.execute(query, (group_id,))
    disciplines = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(disciplines)

@app.route('/api/groups/<int:group_id>/disciplines/save', methods=['POST'])
def save_group_disciplines(group_id):
    """Сохранить выбранные дисциплины"""
    data = request.json
    selected_disciplines = data.get('selected_disciplines', [])
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        # Получаем текущий период
        cursor.execute("SELECT id FROM periods WHERE is_current = 1 LIMIT 1")
        period = cursor.fetchone()
        period_id = period[0] if period else 1
        
        # Удаляем старые
        cursor.execute("""
            DELETE FROM group_disciplines 
            WHERE group_id = %s AND period_id = %s
        """, (group_id, period_id))
        
        # Добавляем новые
        for disc_id in selected_disciplines:
            cursor.execute("""
                INSERT INTO group_disciplines (group_id, discipline_id, period_id, is_selected)
                VALUES (%s, %s, %s, 1)
            """, (group_id, disc_id, period_id))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Дисциплины сохранены'
        })
        
    except Error as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/disciplines/search')
def search_disciplines():
    """Поиск дисциплин"""
    query = request.args.get('q', '')
    department_id = request.args.get('department_id', type=int)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    sql = """
        SELECT d.id, d.name, dep.name as department_name
        FROM disciplines d
        JOIN departments dep ON d.department_id = dep.id
        WHERE d.name LIKE %s
    """
    params = [f'%{query}%']
    
    if department_id:
        sql += " AND d.department_id = %s"
        params.append(department_id)
    
    sql += " ORDER BY d.name LIMIT 20"
    
    cursor.execute(sql, params)
    disciplines = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(disciplines)

@app.route('/api/group-disciplines/add', methods=['POST'])
def add_discipline():
    """Добавить дисциплину группе"""
    data = request.json
    group_id = data.get('group_id')
    discipline_id = data.get('discipline_id')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM periods WHERE is_current = 1 LIMIT 1")
        period = cursor.fetchone()
        period_id = period[0] if period else 1
        
        cursor.execute("""
            INSERT INTO group_disciplines (group_id, discipline_id, period_id, is_selected)
            VALUES (%s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE is_selected = 1
        """, (group_id, discipline_id, period_id))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Дисциплина добавлена'})
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/group-disciplines/remove', methods=['POST'])
def remove_discipline():
    """Удалить дисциплину у группы"""
    data = request.json
    group_id = data.get('group_id')
    discipline_id = data.get('discipline_id')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM periods WHERE is_current = 1 LIMIT 1")
        period = cursor.fetchone()
        period_id = period[0] if period else 1
        
        cursor.execute("""
            DELETE FROM group_disciplines 
            WHERE group_id = %s AND discipline_id = %s AND period_id = %s
        """, (group_id, discipline_id, period_id))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Дисциплина удалена'})
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Московский политех - Выбор дисциплин</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            color: #1a1a2e;
        }
        
        /* Шапка */
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .logo p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .user-details {
            text-align: right;
        }
        
        .user-name {
            display: block;
            font-weight: 600;
            font-size: 16px;
        }
        
        .user-role {
            font-size: 12px;
            opacity: 0.8;
        }
        
        /* Навигация */
        .navigation {
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-bottom: 1px solid #e0e6ed;
        }
        
        .nav-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
            display: flex;
            gap: 30px;
        }
        
        .nav-btn {
            padding: 15px 20px;
            background: none;
            border: none;
            font-size: 16px;
            font-weight: 500;
            color: #6c757d;
            cursor: pointer;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        
        .nav-btn:hover, .nav-btn.active {
            color: #2a5298;
            border-bottom-color: #2a5298;
        }
        
        /* Основной контент */
        .main-content {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 30px;
        }
        
        .content-header {
            background: white;
            padding: 25px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .content-header h2 {
            font-size: 24px;
            margin-bottom: 20px;
            color: #1e3c72;
        }
        
        .filters {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .filter-group label {
            font-weight: 500;
            color: #6c757d;
            min-width: 120px;
        }
        
        .filter-group select {
            padding: 10px 15px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            font-size: 14px;
            min-width: 250px;
            cursor: pointer;
            background: white;
        }
        
        /* Таблица */
        .groups-table-container {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .table-header {
            padding: 20px 25px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .table-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .table-title h3 {
            font-size: 18px;
            color: #2c3e50;
        }
        
        .group-count {
            background: #e9ecef;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #495057;
        }
        
        .collapse-btn {
            background: none;
            border: none;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #6c757d;
            cursor: pointer;
            font-size: 14px;
            padding: 6px 12px;
            border-radius: 6px;
        }
        
        .collapse-btn:hover {
            background: #e9ecef;
        }
        
        .table-wrapper {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: #f8f9fa;
            padding: 15px 20px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }
        
        td {
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .group-name {
            font-weight: 600;
            color: #2a5298;
        }
        
        .disciplines-badge {
            display: inline-block;
            background: #e7f3ff;
            color: #0066cc;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 2px;
        }
        
        .edit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        
        .edit-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .save-all-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 100;
        }
        
        /* Модальное окно */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: white;
            border-radius: 12px;
            max-width: 700px;
            width: 90%;
            max-height: 85vh;
            overflow: auto;
        }
        
        .modal-header {
            padding: 20px 25px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8f9fa;
        }
        
        .modal-header h3 {
            font-size: 20px;
            color: #1e3c72;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 28px;
            cursor: pointer;
            color: #6c757d;
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .selected-disciplines-list {
            margin-bottom: 30px;
        }
        
        .selected-disciplines-list h4 {
            margin-bottom: 15px;
            color: #28a745;
        }
        
        .discipline-item-selected {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .discipline-name {
            font-weight: 500;
        }
        
        .remove-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .add-discipline-section {
            border-top: 1px solid #dee2e6;
            padding-top: 20px;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .search-box input {
            flex: 1;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .search-box button {
            padding: 10px 20px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        
        .search-results {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .search-result-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .add-discipline-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 4px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .modal-footer {
            padding: 20px 25px;
            border-top: 1px solid #dee2e6;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            background: #f8f9fa;
        }
        
        .btn-primary, .btn-secondary {
            padding: 10px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        
        .toast {
            position: fixed;
            bottom: 100px;
            right: 30px;
            background: #28a745;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            display: none;
            z-index: 1000;
        }
        
        @media (max-width: 768px) {
            .header-content, .nav-content, .main-content {
                padding: 0 15px;
            }
            .filter-group {
                flex-direction: column;
                align-items: flex-start;
            }
            th, td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <h1>Московский политех</h1>
                <p>Проверка остаточных знаний</p>
            </div>
            <div class="user-info">
                <div class="user-avatar">👨‍🏫</div>
                <div class="user-details">
                    <span class="user-name">{{ user.name }}</span>
                    <span class="user-role">{{ user.role }}</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="navigation">
        <div class="nav-content">
            <button class="nav-btn active">📚 Выбор дисциплин</button>
            <button class="nav-btn">👥 Выбор преподавателей</button>
        </div>
    </div>
    
    <div class="main-content">
        <div class="content-header">
            <h2>Выбор дисциплин</h2>
            <div class="filters">
                <div class="filter-group">
                    <label>Факультет/Институт:</label>
                    <select id="facultyFilter">
                        <option value="">Все факультеты</option>
                        {% for f in faculties %}
                        <option value="{{ f.id }}">{{ f.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Кафедра:</label>
                    <select id="departmentFilter">
                        <option value="">Все кафедры</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="groups-table-container">
            <div class="table-header">
                <div class="table-title">
                    <h3>Учебные группы</h3>
                    <span class="group-count" id="groupCount">0</span>
                </div>
                <button class="collapse-btn" id="collapseBtn">▲ Свернуть</button>
            </div>
            <div class="table-wrapper" id="groupsTableWrapper">
                <table id="groupsTable">
                    <thead>
                        <tr>
                            <th>Факультет</th>
                            <th>Кафедра</th>
                            <th>Группа</th>
                            <th>Выбранные дисциплины</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody id="groupsTableBody">
                        <tr><td colspan="5" class="loading">⏳ Загрузка данных...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <button class="save-all-btn" id="saveAllBtn">💾 Сохранить все изменения</button>
    <div class="toast" id="toast">✓ Изменения сохранены</div>
    
    <!-- Модальное окно -->
    <div class="modal" id="disciplinesModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">Редактирование списка дисциплин</h3>
                <button class="close-modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="selected-disciplines-list">
                    <h4>📖 Выбранные дисциплины</h4>
                    <div id="selectedDisciplinesList"></div>
                </div>
                <div class="add-discipline-section">
                    <h4>➕ Добавить дисциплину</h4>
                    <div class="search-box">
                        <input type="text" id="disciplineSearch" placeholder="Поиск дисциплины...">
                        <button id="searchBtn">Найти</button>
                    </div>
                    <div id="searchResults" class="search-results"></div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" id="closeModalBtn">Закрыть</button>
                <button class="btn-primary" id="saveModalBtn">Сохранить</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentGroup = null;
        let currentDisciplines = [];
        let pendingChanges = {};
        
        // Загрузка кафедр
        async function loadDepartments(facultyId) {
            const response = await fetch(`/api/departments?faculty_id=${facultyId || ''}`);
            const departments = await response.json();
            const select = document.getElementById('departmentFilter');
            select.innerHTML = '<option value="">Все кафедры</option>';
            departments.forEach(dept => {
                select.innerHTML += `<option value="${dept.id}">${dept.name}</option>`;
            });
        }
        
        // Загрузка групп
        async function loadGroups() {
            const departmentId = document.getElementById('departmentFilter').value;
            let url = '/api/groups';
            if (departmentId) url += `?department_id=${departmentId}`;
            
            const response = await fetch(url);
            const groups = await response.json();
            document.getElementById('groupCount').textContent = groups.length;
            
            const tbody = document.getElementById('groupsTableBody');
            if (groups.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">📭 Нет данных</td></tr>';
                return;
            }
            
            tbody.innerHTML = '';
            for (const group of groups) {
                const selectedDisc = pendingChanges[group.id] || [];
                const discCount = selectedDisc.length;
                
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${group.faculty_name}</td>
                    <td>${group.department_name}</td>
                    <td class="group-name">${group.name}</td>
                    <td id="disc-cell-${group.id}">
                        ${discCount > 0 ? 
                            `<span class="disciplines-badge">Выбрано: ${discCount}</span>` : 
                            '<span style="color:#999">Не выбрано</span>'}
                    </td>
                    <td><button class="edit-btn" onclick="openModal(${group.id}, '${group.name}')">✏️ Редактировать</button></td>
                `;
            }
        }
        
        // Загрузка выбранных дисциплин для группы
        async function loadSelectedDisciplines(groupId) {
            const response = await fetch(`/api/groups/${groupId}/selected-disciplines`);
            return await response.json();
        }
        
        // Открытие модального окна
        async function openModal(groupId, groupName) {
            currentGroup = groupId;
            document.getElementById('modalTitle').innerHTML = `Редактирование списка дисциплин - ${groupName}`;
            
            // Загружаем сохраненные дисциплины
            const saved = await loadSelectedDisciplines(groupId);
            currentDisciplines = pendingChanges[groupId] ? [...pendingChanges[groupId]] : saved.map(d => d.id);
            
            renderSelectedDisciplines();
            document.getElementById('disciplinesModal').style.display = 'flex';
        }
        
        // Отображение выбранных дисциплин
        function renderSelectedDisciplines() {
            const container = document.getElementById('selectedDisciplinesList');
            if (currentDisciplines.length === 0) {
                container.innerHTML = '<p style="color:#999">Дисциплины не выбраны</p>';
                return;
            }
            
            container.innerHTML = '<div style="max-height:300px; overflow-y:auto">';
            for (const discId of currentDisciplines) {
                container.innerHTML += `
                    <div class="discipline-item-selected" data-id="${discId}">
                        <span class="discipline-name">Дисциплина #${discId}</span>
                        <button class="remove-btn" onclick="removeDisciplineFromList(${discId})">Удалить</button>
                    </div>
                `;
            }
            container.innerHTML += '</div>';
        }
        
        // Удаление дисциплины из списка
        function removeDisciplineFromList(disciplineId) {
            currentDisciplines = currentDisciplines.filter(id => id !== disciplineId);
            renderSelectedDisciplines();
        }
        
        // Поиск дисциплин
        async function searchDisciplines() {
            const query = document.getElementById('disciplineSearch').value;
            if (!query.trim()) return;
            
            const departmentId = document.getElementById('departmentFilter').value;
            let url = `/api/disciplines/search?q=${encodeURIComponent(query)}`;
            if (departmentId) url += `&department_id=${departmentId}`;
            
            const response = await fetch(url);
            const results = await response.json();
            
            const container = document.getElementById('searchResults');
            if (results.length === 0) {
                container.innerHTML = '<p style="color:#999">Ничего не найдено</p>';
                return;
            }
            
            container.innerHTML = '';
            for (const disc of results) {
                const isSelected = currentDisciplines.includes(disc.id);
                container.innerHTML += `
                    <div class="search-result-item">
                        <div>
                            <strong>${disc.name}</strong><br>
                            <small style="color:#666">${disc.department_name}</small>
                        </div>
                        ${!isSelected ? 
                            `<button class="add-discipline-btn" onclick="addDisciplineToList(${disc.id})">+ Добавить</button>` :
                            '<span style="color:#28a745">✓ Добавлена</span>'}
                    </div>
                `;
            }
        }
        
        // Добавление дисциплины в список
        function addDisciplineToList(disciplineId) {
            if (!currentDisciplines.includes(disciplineId)) {
                currentDisciplines.push(disciplineId);
                renderSelectedDisciplines();
                document.getElementById('disciplineSearch').value = '';
                document.getElementById('searchResults').innerHTML = '';
            }
        }
        
        // Сохранение дисциплин для текущей группы
        async function saveCurrentGroupDisciplines() {
            const response = await fetch(`/api/groups/${currentGroup}/disciplines/save`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({selected_disciplines: currentDisciplines})
            });
            
            const result = await response.json();
            if (result.success) {
                pendingChanges[currentGroup] = [...currentDisciplines];
                updateGroupDisplay(currentGroup);
                showToast('Дисциплины сохранены');
                return true;
            }
            return false;
        }
        
        // Обновление отображения группы
        function updateGroupDisplay(groupId) {
            const discCell = document.getElementById