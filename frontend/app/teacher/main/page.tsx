"use client";

import Navbar from "@/components/navbar/Navbar";
import Table from "@/components/table/Table";

const table_1 = [
    {
        stage: "Контроль знаний", date: "30.05.2025 - 28.06.2025"
    },
    {
        stage: "Сдача электронных отчетов", date: "до 05.07.2025"
    },
    {
        stage: "Сдача бумажных отчетов", date: "до 15.07.2025"
    },
]

const table_2 = [
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Сети и телекоммуникации",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    },
    {
        groupe: "221-111",
        subject: "Back-end разработка",
        date: "15.06.2024",
        time: "12:20",
        stage: "Согласованно"
    }
]

export default function Home() {
    return (
        <div className="bg-container">
            <div className="bg-gradient"></div>
            <Navbar
                title="Проверка остаточных знаний"
                linkOptions={[
                    { label: "Согласование дат", href: "/csh/teacher/main" },
                    { label: "Отчеты", href: "/csh/teacher/report" }
                ]}
                name="Иван"
                surname="Иванов"
                lastname="Иванович"
            />
            <div className="main-container">
                <p className="title text-bold">Сроки проведения тестирования</p>
                <Table
                    columns={[
                    {
                        header: 'Этап',
                        accessor: 'stage'
                    },
                    {
                        header: 'Дата',
                        accessor: 'date'
                    }
                    ]}
                    data={table_1}
                />
                <p className="title text-bold">Согласование дат проведения проверки остаточных знаний</p>
                <Table
                    columns={[
                    {
                        header: 'Группа',
                        accessor: 'groupe'
                    },
                    {
                        header: 'Дисциплина',
                        accessor: 'subject'
                    },
                    {
                        header: 'Дата проведения',
                        accessor: 'date'
                    },
                    {
                        header: 'Время проведения',
                        accessor: 'time'
                    },
                    {
                        header: 'Стадия соглосования',
                        accessor: 'stage'
                    }
                ]}
                    data={table_2}
                />
            </div>
        </div>
    );
}
