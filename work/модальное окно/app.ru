from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'secret-key-for-session'  # Добавьте секретный ключ

# демо-данные
GROUPS = [
    {"id": "221-111", "course": 3, "prev": [0, 1, 1], "current": 0, "plan": None},
    {"id": "221-112", "course": 3, "prev": [0, 1, 1], "current": 1, "plan": "spr26"},
    {"id": "221-113", "course": 3, "prev": [0, 1, 1], "current": 1, "plan": "spr26"},
    {"id": "221-114", "course": 3, "prev": [0, 1, 1], "current": 0, "plan": "aut25"},
]

# Используем сессию для хранения данных между запросами
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            print("=== ПОЛУЧЕНЫ ДАННЫЕ ФОРМЫ ===")
            print(f"Метод: {request.method}")
            print(f"Content-Type: {request.content_type}")
            print(f"Всего полей: {len(request.form)}")
            
            if not request.form:
                print("ВНИМАНИЕ: Форма пустая!")
                # Проверяем raw data
                print(f"Raw data: {request.get_data()}")
            else:
                for key, value in request.form.items():
                    print(f"{key}: {value}")
            
            print("=============================")
            
            # обновляем состояния по форме
            for g in GROUPS:
                gid = g["id"]
                # предыдущие три (чекбоксы)
                v23 = bool(request.form.get(f"prev_{gid}_v23"))
                o23 = bool(request.form.get(f"prev_{gid}_o23"))
                v24 = bool(request.form.get(f"prev_{gid}_v24"))
                g["prev"] = [1 if v23 else 0, 1 if o23 else 0, 1 if v24 else 0]

                # текущее (чекбокс)
                cur = bool(request.form.get(f"cur_{gid}"))
                g["current"] = 1 if cur else 0

                # план (радио)
                plan = request.form.get(f"plan_{gid}")
                if plan in ("aut25", "spr26"):
                    g["plan"] = plan
                else:
                    g["plan"] = None
                
                # Сохраняем выбранные дисциплины
                subject1 = request.form.get(f"subjects_{gid}_1", "")
                subject2 = request.form.get(f"subjects_{gid}_2", "")
                if subject1 or subject2:
                    if 'group_subjects' not in session:
                        session['group_subjects'] = {}
                    session['group_subjects'][gid] = [subject1, subject2]
                    print(f"Для группы {gid} выбраны дисциплины: {subject1}, {subject2}")
            
            # Сохраняем группы в сессии
            session['groups'] = GROUPS
            
        except Exception as e:
            print(f"Ошибка обработки формы: {e}")
            import traceback
            traceback.print_exc()

        return redirect(url_for("index"))
    
    # Восстанавливаем данные из сессии при GET запросе
    if 'groups' in session:
        groups_to_render = session['groups']
    else:
        groups_to_render = GROUPS
    
    return render_template("index.html", groups=groups_to_render)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
