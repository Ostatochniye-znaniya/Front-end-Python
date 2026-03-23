USE knowledge_test_db;

-- Заполнение таблицы statuses +
INSERT INTO statuses VALUES (1, "На рассмотрении");
INSERT INTO statuses VALUES (2, "Активен");
INSERT INTO statuses VALUES (3, "Неактивен");
INSERT INTO statuses VALUES (4, "На удалении");

-- Заполнение таблицы roles +
INSERT INTO roles VALUES (1, "Лицо принимающее решение");
INSERT INTO roles VALUES (2, "Ответственный за факультет");
INSERT INTO roles VALUES (3, "Заведующий кафедрой");
INSERT INTO roles VALUES (4, "Преподаватель");

-- Заполнение таблицы faculties +
INSERT INTO faculties VALUES (1, "Факультет информационных технологий");
INSERT INTO faculties VALUES (2, "Транспортный факультет");
INSERT INTO faculties VALUES (3, "Факультет машиностроения");
INSERT INTO faculties VALUES (4, "Факультет химической технологии и биотехнологии");
INSERT INTO faculties VALUES (5, "Факультет экономики и управления");

-- Заполнение таблицы users +
INSERT INTO users VALUES (1, "Шишкин Анатолий Витальевич", "aaa@mospolytech.ru", "12345678", 2, 1);
INSERT INTO users VALUES (2, "Смирнов Алексей Иванович", "bbb@mospolytech.ru", "9876543", 2, 2);
INSERT INTO users VALUES (3, "Волкова Анна Игоревна", "ccc@mospolytech.ru", "1289056", 2, 3);
INSERT INTO users VALUES (4, "Крестовников Павел Михайлович", "ddd@mospolytech.ru", "345621", 2, 2);
INSERT INTO users VALUES (5, "Иванова Анастасия Леонидовна", "eee@yandex.ru", "9090876", 2, 1);
INSERT INTO users VALUES (6, "Кузнецова Василиса Александровна", "fff@mospolytech.ru", "34432123", 2, 4);
INSERT INTO users VALUES (7, "Соколов Александр Васильевич", "ggg@yandex.ru", "1209998", 2, 5);
INSERT INTO users VALUES (8, "Петрова Ксения Павловна", "hhh@mospolytech.ru", "4554378", 2, 5);
INSERT INTO users VALUES (9, "Васильев Юрий Викторович", "jjj@mospolytech.ru", "89987123", 2, 4);
INSERT INTO users VALUES (10, "Попов Антон Степанович", "kkk@yandex.ru", "0043871", 2, 3);

-- Заполнение таблицы departments +
INSERT INTO departments VALUES (1, "Прикладная информатика", 1);
INSERT INTO departments VALUES (2, "Информатика и информационные технологии", 1);
INSERT INTO departments VALUES (3, "Динамика, прочность машин и сопротивление материалов", 2);
INSERT INTO departments VALUES (4, "Наземные транспортные средства", 2);
INSERT INTO departments VALUES (5, "Металлургия", 3);
INSERT INTO departments VALUES (6, "Технологии и оборудование машиностроения", 3);
INSERT INTO departments VALUES (7, "Процессы и аппараты химической технологии", 4);
INSERT INTO departments VALUES (8, "Экологическая безопасность технических систем", 4);
INSERT INTO departments VALUES (9, "Менеджмент", 5);
INSERT INTO departments VALUES (10, "Экономика и организация", 5);

-- Заполнение таблицы disciplines +
INSERT INTO disciplines VALUES (1, "Языки программирования", 1);
INSERT INTO disciplines VALUES (2, "Основы веб-технологий", 2);
INSERT INTO disciplines VALUES (3, "Разработка веб-приложений", 2);
INSERT INTO disciplines VALUES (4, "Сопротивление материалов", 3);
INSERT INTO disciplines VALUES (5, "Современные транспортные средства", 4);
INSERT INTO disciplines VALUES (6, "Теория обработки металлов давлением", 5);
INSERT INTO disciplines VALUES (7, "Теория и технология прокатки", 6);
INSERT INTO disciplines VALUES (8, "Процессы и аппараты химической технологии", 7);
INSERT INTO disciplines VALUES (9, "Экология отрасли", 8);
INSERT INTO disciplines VALUES (10, "Экономика", 10);

-- Заполнение таблицы study_programs +
INSERT INTO study_programs VALUES (1, "Веб-технологии", 1, "ВЕБ");
INSERT INTO study_programs VALUES (2, "Системная и программная инженерия", 1, "СИПИ");
INSERT INTO study_programs VALUES (3, "Интеллектуальные системы управления транспортом", 3, "ИСУТ");
INSERT INTO study_programs VALUES (4, "Транспортный и промышленный дизайн", 4, "ТИПД");
INSERT INTO study_programs VALUES (5, "Роботы и роботехнические комплексы", 6, "РРК");
INSERT INTO study_programs VALUES (6, "Автоматизированное производство химических предприятий", 7, "АвтоХим");
INSERT INTO study_programs VALUES (7, "Управление бизнес-процессами", 9, "УпрБП");

-- Заполнение таблицы study_groups +
INSERT INTO study_groups VALUES (1, "231-3210", 2);
INSERT INTO study_groups VALUES (2, "334-223", 5);
INSERT INTO study_groups VALUES (3, "123-325", 6);
INSERT INTO study_groups VALUES (4, "234-121", 3);
INSERT INTO study_groups VALUES (5, "221-321", 1);

-- Заполнение таблицы reports +
INSERT INTO reports VALUES (1, 8, 6, "../folder1/folder2/result1.docx", 0, 0, 1, 0, 1);
INSERT INTO reports VALUES (2, 6, 10, "../folder3/folder4/result2.docx", 1, 1, 1, 1, 2);
INSERT INTO reports VALUES (3, 1, 1, "../folder5/folder6/result3.docx", 1, 0, 1, 0, 3);
INSERT INTO reports VALUES (4, 2, 5, "../folder7/folder8/result4.docx", 1, 1, 1, 1, 4);
INSERT INTO reports VALUES (5, 3, 1, "../folder9/folder10/result5.docx", 0, 0, 1, 0, 5);

-- Заполнение таблицы testing 
INSERT INTO testing VALUES (1, 3, 8, "2023-10-24", "14:30:00", "Завершено", "Тестирование было проведено согласно установленным дате и времени", 1, 1);
INSERT INTO testing VALUES (2, 2, 6, "2023-10-26", "12:10:00", "Завершено", "Тестирование было проведено согласно установленным дате и времени", 2, 2);
INSERT INTO testing VALUES (3, 1, 3, "2024-11-23", "10:40:00", "Завершено", "Тестирование было проведено согласно установленным дате и времени", 5, 5);
INSERT INTO testing VALUES (4, 5, 1, "2024-11-25", "9:00:00", "Завершено", "Тестирование было проведено согласно установленным дате и времени", 3, 3);
INSERT INTO testing VALUES (5, 5, 2, "2024-11-26", "16:00:00", "Завершено", "Тестирование было проведено согласно установленным дате и времени", 4, 4);

-- Заполнение таблицы discipline_teacher +
INSERT INTO discipline_teacher VALUES (1, 8, 6);
INSERT INTO discipline_teacher VALUES (2, 6, 10);
INSERT INTO discipline_teacher VALUES (3, 1, 1);
INSERT INTO discipline_teacher VALUES (4, 2, 5);
INSERT INTO discipline_teacher VALUES (5, 3, 1);
INSERT INTO discipline_teacher VALUES (6, 4, 3);
INSERT INTO discipline_teacher VALUES (7, 5, 2);
INSERT INTO discipline_teacher VALUES (8, 7, 10);
INSERT INTO discipline_teacher VALUES (9, 9, 9);
INSERT INTO discipline_teacher VALUES (10, 10, 7);

-- Заполнение таблицы user_role +
INSERT INTO user_role VALUES (1, 1, 2);
INSERT INTO user_role VALUES (2, 2, 1);
INSERT INTO user_role VALUES (3, 3, 2);
INSERT INTO user_role VALUES (4, 4, 2);
INSERT INTO user_role VALUES (5, 5, 3);
INSERT INTO user_role VALUES (6, 6, 4);
INSERT INTO user_role VALUES (7, 6, 3);
INSERT INTO user_role VALUES (8, 7, 2);
INSERT INTO user_role VALUES (9, 8, 3);
INSERT INTO user_role VALUES (10, 9, 2);
INSERT INTO user_role VALUES (11, 10, 4);

-- Заполнениие таблицы semesters +
INSERT INTO semesters VALUES (1, '01.01.2023');
INSERT INTO semesters VALUES (2, '01.09.2024');
INSERT INTO semesters VALUES (3, '01.01.2024');
INSERT INTO semesters VALUES (4, '01.09.2025');
INSERT INTO semesters VALUES (5, '01.01.2025');

-- Заполнение таблицы students +
INSERT INTO students VALUES (1, 'Волков Иван Фёдорович', 1, 5, 'Допущен');
INSERT INTO students VALUES (2, 'Птицина Инна Алексеевна', 2, 1, 'Не допущен');
INSERT INTO students VALUES (3, 'Петров Анатолий Юрьевич', 2, 1, 'Допущен');
INSERT INTO students VALUES (4, 'Дмитрова Ксения Ивановна', 4, 4, 'Допущен');
INSERT INTO students VALUES (5, 'Арсеньев Фёдор Александрович', 3, 3, 'Не проводилась');