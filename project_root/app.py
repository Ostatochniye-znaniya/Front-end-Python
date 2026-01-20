from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ========== MOCK ROLE ==========
# Возможные значения:
# head — заведующий кафедрой
# faculty — ответственный факультета
# teacher — преподаватель
# guest — гость

CURRENT_ROLE = "head"

# ========== Моки (в реальном API будут заменены) ==========

GROUPS = [
    {"id": "221-321", "name": "221-321"},
    {"id": "221-322", "name": "221-322"},
    {"id": "221-323", "name": "221-323"},
]

DISCIPLINES = [
    {"id": "disc_web", "name": "Веб-разработка"},
    {"id": "disc_db", "name": "Базы данных"},
    {"id": "disc_ai", "name": "Искусственный интеллект"},
]

SUBDIVISIONS = [
    {"id": "fit", "name": "ФИТ"},
    {"id": "fkb", "name": "ФБК"},
    {"id": "fmm", "name": "ФММ"},
]

TEACHERS = [
    {"id": "t1", "name": "Верещагин В.Ю."},
    {"id": "t2", "name": "Петрова А.А."},
    {"id": "t3", "name": "Иванов И.И."},
]

# ===================== 2.5.1 — Выбор групп и дисциплин =====================

GROUPS_SELECTION = [
    {
        "id": "221-321",
        "profile": "Веб-технологии",
        "participates": False,
        "discipline1_id": "",
        "discipline2_id": "",
        "teacher_id": "",
        "date": "",
        "time": "",
    },
    {
        "id": "221-322",
        "profile": "Веб-технологии",
        "participates": True,
        "discipline1_id": "disc_web",
        "discipline2_id": "disc_db",
        "teacher_id": "t1",
        "date": "2025-06-22",
        "time": "12:00",
    },
    {
        "id": "221-323",
        "profile": "Интеграция и программирование в САПР",
        "participates": False,
        "discipline1_id": "",
        "discipline2_id": "",
        "teacher_id": "",
        "date": "",
        "time": "",
    },
]

@app.route("/groups-selection", methods=["GET", "POST"])
def groups_selection():
    if request.method == "POST":
        for g in GROUPS_SELECTION:
            gid = g["id"]

            g["participates"] = bool(request.form.get(f"participates_{gid}"))
            g["discipline1_id"] = request.form.get(f"disc1_{gid}", "")
            g["discipline2_id"] = request.form.get(f"disc2_{gid}", "")
            g["teacher_id"] = request.form.get(f"teacher_{gid}", "")
            g["date"] = request.form.get(f"date_{gid}", "")
            g["time"] = request.form.get(f"time_{gid}", "")

        print("=== 2.5.1 Сохранены данные ===")
        print(GROUPS_SELECTION)

        return redirect(url_for("groups_selection"))

    return render_template(
        "groups_selection.html",
        groups=GROUPS_SELECTION,
        disciplines=DISCIPLINES,
        teachers=TEACHERS,
        role=CURRENT_ROLE,
    )

# ===================== 2.5.2 — Заявка на чужой факультет =====================

FOREIGN_REQUESTS = []

@app.route("/foreign-request", methods=["GET", "POST"])
def foreign_request():
    if request.method == "POST":
        data = {
            "group_id": request.form.get("group"),
            "discipline_id": request.form.get("discipline"),
            "executor_subdivision_id": request.form.get("executor_subdivision"),
            "comment": request.form.get("comment"),
        }

        FOREIGN_REQUESTS.append(data)

        print("=== Новая заявка создана ===")
        print(data)

        return redirect(url_for("foreign_request_success"))

    return render_template(
        "foreign_request.html",
        groups=GROUPS,
        disciplines=DISCIPLINES,
        subdivisions=SUBDIVISIONS,
    )

@app.route("/foreign-request/success")
def foreign_request_success():
    return render_template("foreign_request_success.html")

# ===================== 2.6 — Входящие заявки =====================

INCOMING_REQUESTS = [
    {
        "id": 1,
        "from_subdivision": "ФИТ",
        "group": "221-321",
        "discipline": "Проектирование интерфейсов",
        "status": "requested"
    },
    {
        "id": 2,
        "from_subdivision": "ФБК",
        "group": "221-322",
        "discipline": "Базы данных",
        "status": "requested"
    },
]

@app.route("/incoming-requests", methods=["GET", "POST"])
def incoming_requests():
    if request.method == "POST":
        req_id = int(request.form.get("request_id"))
        teacher_id = request.form.get("teacher")
        date = request.form.get("date")
        time = request.form.get("time")

        for req in INCOMING_REQUESTS:
            if req["id"] == req_id:
                req["status"] = "approved"
                req["assigned_teacher"] = teacher_id
                req["date"] = date
                req["time"] = time
                break

        print("=== Заявка обработана ===")
        print(req)

        return redirect(url_for("incoming_requests"))

    return render_template(
        "incoming_requests.html",
        requests=INCOMING_REQUESTS,
        teachers=TEACHERS
    )

# ===================== 2.6 — График проверок =====================

SCHEDULE = [
    {
        "group": "221-321",
        "discipline": "ОИБ",
        "teacher": "Иванов И.И.",
        "date": "2025-06-12",
        "time": "10:00",
        "status": "confirmed",
    },
    {
        "group": "221-322",
        "discipline": "Базы данных",
        "teacher": "Верещагин В.Ю.",
        "date": "2025-06-22",
        "time": "12:00",
        "status": "confirmed",
    },
    {
        "group": "221-323",
        "discipline": "Веб-разработка",
        "teacher": "Петрова А.А.",
        "date": "2025-06-18",
        "time": "09:00",
        "status": "planned",
    },
]

@app.route("/schedule", methods=["GET"])
def schedule_page():
    filter_group = request.args.get("group", "").strip()
    filter_disc = request.args.get("discipline", "").strip()
    filter_teacher = request.args.get("teacher", "").strip()

    filtered = []
    for item in SCHEDULE:
        if filter_group and filter_group not in item["group"]:
            continue
        if filter_disc and filter_disc not in item["discipline"]:
            continue
        if filter_teacher and filter_teacher not in item["teacher"]:
            continue
        filtered.append(item)

    return render_template(
        "schedule.html",
        schedule=filtered,
        filter_group=filter_group,
        filter_disc=filter_disc,
        filter_teacher=filter_teacher,
    )

# ===================== RUN =====================

if __name__ == "__main__":
    app.run(debug=True)
