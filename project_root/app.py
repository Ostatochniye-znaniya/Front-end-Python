from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# демо-справочники
DISCIPLINES = [
    {"id": "disc_web", "name": "Веб-разработка"},
    {"id": "disc_db", "name": "Базы данных"},
    {"id": "disc_mobile", "name": "Разработка мобильных приложений"},
    {"id": "disc_ai", "name": "Искусственные нейронные сети"},
]

TEACHERS = [
    {"id": "t_veresh", "name": "Верещагин В.Ю."},
    {"id": "t_beres", "name": "Береснева Я.В."},
    {"id": "t_petrov", "name": "Петров И.А."},
]

# демо-группы (можешь взять реальные из таблицы ФИТ)
GROUPS = [
    {
        "id": "221-321",
        "profile": "Веб-технологии",
        "participates": False,
        "discipline1_id": None,
        "discipline2_id": None,
        "teacher_id": None,
        "date": None,
        "time": None,
    },
    {
        "id": "221-322",
        "profile": "Веб-технологии",
        "participates": True,
        "discipline1_id": "disc_web",
        "discipline2_id": "disc_db",
        "teacher_id": "t_veresh",
        "date": "2024-06-22",
        "time": "12:00",
    },
    {
        "id": "221-323",
        "profile": "Интеграция и программирование в САПР",
        "participates": False,
        "discipline1_id": None,
        "discipline2_id": None,
        "teacher_id": None,
        "date": None,
        "time": None,
    },
]


@app.route("/", methods=["GET", "POST"])
def groups_selection():
    if request.method == "POST":
        # обновляем состояния по форме
        for g in GROUPS:
            gid = g["id"]

            # участвует / не участвует
            participates = bool(request.form.get(f"participates_{gid}"))
            g["participates"] = participates

            # дисциплины
            disc1 = request.form.get(f"disc1_{gid}") or None
            disc2 = request.form.get(f"disc2_{gid}") or None
            g["discipline1_id"] = disc1
            g["discipline2_id"] = disc2

            # преподаватель
            teacher_id = request.form.get(f"teacher_{gid}") or None
            g["teacher_id"] = teacher_id

            # дата и время
            date_val = request.form.get(f"date_{gid}") or ""
            time_val = request.form.get(f"time_{gid}") or ""

            g["date"] = date_val if date_val else None
            g["time"] = time_val if time_val else None

        # здесь пока просто выводим результат в консоль
        print("=== Сохранённые значения ===")
        for g in GROUPS:
            print(g)

        # редирект, чтобы избежать повторного POST при обновлении
        return redirect(url_for("groups_selection"))

    return render_template(
        "groups_selection.html",
        groups=GROUPS,
        disciplines=DISCIPLINES,
        teachers=TEACHERS,
    )


if __name__ == "__main__":
    app.run(debug=True)
