"use client";

import { Fragment, useState } from "react";

import Navbar from "@/components/navbar/Navbar";

import styles from "./report.module.css";

type ReportStatus = "Сдан" | "Одобрен" | "Не сдан" | "На доработке" | "Требует проверки";

type CheckReport = {
  id: number;
  group: string;
  discipline: string;
  electronicStatus: ReportStatus;
  paperStatus: ReportStatus;
  faculty: string;
  department: string;
  program: string;
  teacher: string;
  electronicFile?: string;
  paperFile?: string;
};

type SummaryReport = {
  id: number;
  title: string;
};

const reportRows: CheckReport[] = [
  {
    id: 1,
    group: "223-111",
    discipline: "Сети и телекоммуникации",
    electronicStatus: "Сдан",
    paperStatus: "Одобрен",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Иванов И. И.",
    electronicFile: "файл.docx",
    paperFile: "файл.docx",
  },
  {
    id: 2,
    group: "223-111",
    discipline: "Сети и телекоммуникации",
    electronicStatus: "Не сдан",
    paperStatus: "Не сдан",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Иванов И. И.",
  },
  {
    id: 3,
    group: "223-111",
    discipline: "Сети и телекоммуникации",
    electronicStatus: "На доработке",
    paperStatus: "Не сдан",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Иванов И. И.",
  },
  {
    id: 4,
    group: "223-111",
    discipline: "Back-end разработка",
    electronicStatus: "Требует проверки",
    paperStatus: "Не сдан",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Иванов И. И.",
    electronicFile: "файл.docx",
  },
  {
    id: 5,
    group: "223-112",
    discipline: "Базы данных",
    electronicStatus: "Сдан",
    paperStatus: "Сдан",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Петрова А. В.",
    electronicFile: "отчет.docx",
    paperFile: "отчет.docx",
  },
  ...Array.from({ length: 35 }, (_, index): CheckReport => ({
    id: index + 6,
    group: `223-${String(113 + index).padStart(3, "0")}`,
    discipline: index % 2 === 0 ? "Сети и телекоммуникации" : "Back-end разработка",
    electronicStatus: index % 3 === 0 ? "Сдан" : index % 3 === 1 ? "Не сдан" : "На доработке",
    paperStatus: index % 2 === 0 ? "Не сдан" : "Сдан",
    faculty: "ФИТ",
    department: "ИИТ",
    program: "ИСТОИУ",
    teacher: "Иванов И. И.",
    electronicFile: index % 3 === 0 ? "файл.docx" : undefined,
    paperFile: index % 2 === 1 ? "файл.docx" : undefined,
  })),
];

const initialSummaryReports: SummaryReport[] = Array.from({ length: 13 }, (_, index) => ({
  id: index + 1,
  title: `Сводный отчет №${String(100 - index).padStart(3, "0")} по результатам Проверки, весна 2024 от 05.05.2024`,
}));

const navLinks = [
  { label: "Главная" },
  { label: "Приказы" },
  { label: "Списки рекомендуемых групп" },
  { label: "Отчеты", href: "/csh/teacher/report" },
  { label: "Настройки доступа" },
];

const statusOptions = ["Не выбрано", "Сдан", "Одобрен", "Не сдан", "На доработке", "Требует проверки"];

export default function ReportPage() {
  const [activeTab, setActiveTab] = useState<"check" | "summary">("check");
  const [expandedReportId, setExpandedReportId] = useState<number | null>(null);
  const [reports, setReports] = useState(reportRows);
  const [summaryReports, setSummaryReports] = useState(initialSummaryReports);
  const [query, setQuery] = useState("");
  const [electronicStatus, setElectronicStatus] = useState("Не выбрано");
  const [paperStatus, setPaperStatus] = useState("Не выбрано");
  const [currentPage, setCurrentPage] = useState(1);

  const visibleReports = reports.filter((report) => {
    const electronicMatches = electronicStatus === "Не выбрано" || report.electronicStatus === electronicStatus;
    const paperMatches = paperStatus === "Не выбрано" || report.paperStatus === paperStatus;
    return electronicMatches && paperMatches;
  });

  const visibleSummaryReports = summaryReports.filter((report) =>
    report.title.toLocaleLowerCase("ru-RU").includes(query.toLocaleLowerCase("ru-RU")),
  );
  const totalPages = Math.max(1, Math.ceil(visibleReports.length / 4));
  const paginatedReports = visibleReports.slice((currentPage - 1) * 4, currentPage * 4);
  const paginationPages = totalPages <= 3
    ? Array.from({ length: totalPages }, (_, index) => index + 1)
    : currentPage < 3
      ? [1, 2, 3]
      : currentPage >= totalPages - 2
        ? [totalPages - 2, totalPages - 1, totalPages]
        : [currentPage, currentPage + 1, currentPage + 2];
  const firstPaginationPage = paginationPages[0];
  const lastPaginationPage = paginationPages[paginationPages.length - 1];

  const updateReportStatus = (id: number, status: ReportStatus) => {
    setReports((currentReports) =>
      currentReports.map((report) =>
        report.id === id ? { ...report, electronicStatus: status } : report,
      ),
    );
  };

  const createSummaryReport = () => {
    const createdAt = new Intl.DateTimeFormat("ru-RU").format(new Date());
    setSummaryReports((currentReports) => [
      {
        id: Date.now(),
        title: `Сводный отчет №101 по результатам Проверки от ${createdAt}`,
      },
      ...currentReports,
    ]);
  };

  return (
    <div className={styles.page}>
      <div className={styles.background} />
      <Navbar
        variant="report"
        title="Проверка остаточных знаний"
        linkOptions={navLinks}
        name="Иван"
        surname="Иванов"
        lastname="Иванович"
      />

      <main className={styles.card}>
        <div className={styles.heading}>
          <h1>Отчёты</h1>
          <div className={styles.tabs} role="tablist" aria-label="Виды отчетов">
            <button
              className={`${styles.tab} ${activeTab === "check" ? styles.tabActive : ""}`}
              type="button"
              role="tab"
              aria-selected={activeTab === "check"}
              aria-controls="check-reports-panel"
              onClick={() => setActiveTab("check")}
            >
              Отчёты проверки
            </button>
            <button
              className={`${styles.tab} ${activeTab === "summary" ? styles.tabActive : ""}`}
              type="button"
              role="tab"
              aria-selected={activeTab === "summary"}
              aria-controls="summary-reports-panel"
              onClick={() => setActiveTab("summary")}
            >
              Сводные отчёты
            </button>
          </div>
        </div>

        {activeTab === "check" ? (
          <section id="check-reports-panel" role="tabpanel" className={styles.checkPanel}>
            <div className={styles.filters}>
              <ReportSelect label="Семестр:" defaultValue="Осень 2024" options={["Осень 2024", "Весна 2024"]} />
              <ReportSelect label="Подразделение (кафедра):" defaultValue="ИИТ" options={["ИИТ", "ИТ", "КИС"]} />
              <ReportSelect label="Факультет/Институт:" defaultValue="ФИТ" options={["ФИТ", "ФФ", "ФХТ"]} />
              <ReportSelect
                label="Статус бумажного отчета:"
                value={paperStatus}
                options={statusOptions}
                onChange={(value) => {
                  setPaperStatus(value);
                  setCurrentPage(1);
                }}
              />
              <ReportSelect
                label="Статус электронного отчета:"
                value={electronicStatus}
                options={statusOptions}
                onChange={(value) => {
                  setElectronicStatus(value);
                  setCurrentPage(1);
                }}
              />
            </div>

            <section className={styles.statistics} aria-label="Статистика по факультету и институту">
              <h2>Статистика по Факультету/Институту:</h2>
              <p>Всего сдано электронных отчетов: 50 из 60</p>
              <p>Всего сдано бумажных отчетов: 20 из 60</p>
            </section>

            <div className={styles.tableScroll}>
              <table className={styles.reportTable}>
                <thead>
                  <tr>
                    <th>Группа <span aria-hidden="true">◆</span></th>
                    <th>Дисциплина</th>
                    <th>Электронный отчет</th>
                    <th>Бумажный отчет</th>
                    <th aria-label="Действия" />
                  </tr>
                </thead>
                <tbody>
                  {paginatedReports.map((report, index) => {
                    const isExpanded = expandedReportId === report.id;
                    const isStriped = index % 2 === 0;
                    return (
                      <Fragment key={report.id}>
                        <tr className={isStriped ? styles.stripedRow : ""}>
                          <td>{report.group}</td>
                          <td>{report.discipline}</td>
                          <td>{report.electronicStatus}</td>
                          <td>{report.paperStatus}</td>
                          <td>
                            <button
                              type="button"
                              className={styles.detailsButton}
                              aria-expanded={isExpanded}
                              onClick={() => setExpandedReportId(isExpanded ? null : report.id)}
                            >
                              {isExpanded ? "Свернуть" : "Подробнее"}
                            </button>
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr className={`${styles.detailsRow} ${isStriped ? styles.stripedDetailsRow : ""}`}>
                            <td colSpan={5}>
                              <div className={styles.details}>
                                <dl>
                                  <div><dt>Факультет/ институт:</dt><dd>{report.faculty}</dd></div>
                                  <div><dt>Подразделение (Кафедра):</dt><dd>{report.department}</dd></div>
                                  <div><dt>Профиль:</dt><dd>{report.program}</dd></div>
                                  <div><dt>Ответственный преподаватель:</dt><dd>{report.teacher}</dd></div>
                                  {report.electronicFile && <div><dt>Электронный отчет:</dt><dd><button type="button" className={styles.fileButton}>{report.electronicFile}</button></dd></div>}
                                </dl>
                                <div className={styles.detailActions}>
                                  <button type="button" className={styles.acceptButton} onClick={() => updateReportStatus(report.id, "Сдан")}>Принять</button>
                                  <button type="button" className={styles.returnButton} onClick={() => updateReportStatus(report.id, "На доработке")}>Вернуть на доработку</button>
                                </div>
                                {report.paperFile && (
                                  <p className={styles.paperFile}>Бумажный отчет: <button type="button" className={styles.fileButton}>{report.paperFile}</button></p>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {visibleReports.length === 0 && <p className={styles.emptyState}>Отчётов с выбранными статусами нет.</p>}

            <nav className={styles.pagination} aria-label="Пагинация отчетов">
              <button type="button" aria-label="Предыдущая страница" disabled={currentPage === 1} onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}>‹</button>
              {firstPaginationPage !== 1 && <button type="button" onClick={() => setCurrentPage(1)}>1</button>}
              {firstPaginationPage > 2 && <span>…</span>}
              {paginationPages.map((page) => <button type="button" key={page} className={page === currentPage ? styles.currentPage : ""} onClick={() => setCurrentPage(page)}>{page}</button>)}
              {lastPaginationPage !== totalPages && <span>…</span>}
              {lastPaginationPage !== totalPages && <button type="button" onClick={() => setCurrentPage(totalPages)}>{totalPages}</button>}
              <button type="button" aria-label="Следующая страница" disabled={currentPage === totalPages} onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}>›</button>
            </nav>
          </section>
        ) : (
          <section id="summary-reports-panel" role="tabpanel" className={styles.summaryPanel}>
            <button type="button" className={styles.createButton} onClick={createSummaryReport}>
              <span className={styles.createIcon} aria-hidden="true">+</span>
              Сформировать новый сводный отчет
            </button>
            <label className={styles.search}>
              <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="6.5" cy="6.5" r="4.5" /><path d="m10 10 4 4" /></svg>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Введите слово" aria-label="Поиск сводного отчета" />
            </label>
            <div className={styles.summaryList}>
              {visibleSummaryReports.map((report) => (
                <button type="button" className={styles.summaryItem} key={report.id}>
                  <span aria-hidden="true">▸</span>{report.title}
                </button>
              ))}
              {visibleSummaryReports.length === 0 && <p className={styles.emptyState}>Сводные отчёты не найдены.</p>}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

type ReportSelectProps = {
  label: string;
  options: string[];
  defaultValue?: string;
  value?: string;
  onChange?: (value: string) => void;
};

function ReportSelect({ label, options, defaultValue, value, onChange }: ReportSelectProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? options[0]);
  const selectedValue = value ?? internalValue;

  return (
    <label className={styles.filter}>
      <span>{label}</span>
      <select
        value={selectedValue}
        onChange={(event) => {
          setInternalValue(event.target.value);
          onChange?.(event.target.value);
        }}
      >
        {options.map((option) => <option key={option}>{option}</option>)}
      </select>
    </label>
  );
}
