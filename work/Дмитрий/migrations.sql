-- 1. Задача 111: RecommendedGroups
-- Рекомендации групп на период (расширение GroupPeriodStatus)
CREATE TABLE IF NOT EXISTS RecommendedGroups (
    id              SERIAL          PRIMARY KEY,
    group_id        INTEGER         NOT NULL,
    period_id       INTEGER         NOT NULL,
    is_recommended  BOOLEAN         NOT NULL DEFAULT FALSE,
    updated_by      INTEGER,                          -- user_id, кто последний менял
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_rg_group
        FOREIGN KEY (group_id)   REFERENCES Groups(id)   ON DELETE CASCADE,
    CONSTRAINT fk_rg_period
        FOREIGN KEY (period_id)  REFERENCES Periods(id)  ON DELETE CASCADE,
    CONSTRAINT fk_rg_user
        FOREIGN KEY (updated_by) REFERENCES Users(id)    ON DELETE SET NULL,

    -- одна запись на пару group + period
    CONSTRAINT uq_rg_group_period UNIQUE (group_id, period_id)
);

CREATE INDEX IF NOT EXISTS idx_rg_period   ON RecommendedGroups(period_id);
CREATE INDEX IF NOT EXISTS idx_rg_group    ON RecommendedGroups(group_id);


-- 2. Задача 118: InspectionSchedules
-- Сформированные графики проверок по факультету и периоду
CREATE TABLE IF NOT EXISTS InspectionSchedules (
    id              SERIAL          PRIMARY KEY,
    faculty_id      INTEGER         NOT NULL,
    period_id       INTEGER         NOT NULL,
    generated_by    INTEGER         NOT NULL,         -- user_id, кто сформировал
    generated_at    TIMESTAMP       NOT NULL DEFAULT NOW(),
    file_link       TEXT,                             -- путь / URL к файлу графика
    status          VARCHAR(20)     NOT NULL DEFAULT 'черновик'
                        CHECK (status IN ('черновик', 'утверждён')),

    CONSTRAINT fk_is_faculty
        FOREIGN KEY (faculty_id)   REFERENCES Faculties(id) ON DELETE CASCADE,
    CONSTRAINT fk_is_period
        FOREIGN KEY (period_id)    REFERENCES Periods(id)   ON DELETE CASCADE,
    CONSTRAINT fk_is_user
        FOREIGN KEY (generated_by) REFERENCES Users(id)     ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_is_faculty ON InspectionSchedules(faculty_id);
CREATE INDEX IF NOT EXISTS idx_is_period  ON InspectionSchedules(period_id);
CREATE INDEX IF NOT EXISTS idx_is_status  ON InspectionSchedules(status);


-- 3. Задача 124: Reports
-- Отчёты преподавателей по назначенным проверкам
CREATE TABLE IF NOT EXISTS Reports (
    id                          SERIAL      PRIMARY KEY,
    inspection_assignment_id    INTEGER     NOT NULL,
    report_data                 JSONB,                -- данные формы отчёта
    file_link                   TEXT,                 -- путь к сгенерированному файлу
    status                      VARCHAR(20) NOT NULL DEFAULT 'черновик'
                                    CHECK (status IN ('черновик', 'на проверке', 'утверждён', 'отклонён')),
    updated_at                  TIMESTAMP   NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_rep_assignment
        FOREIGN KEY (inspection_assignment_id)
            REFERENCES InspectionAssignments(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rep_assignment ON Reports(inspection_assignment_id);
CREATE INDEX IF NOT EXISTS idx_rep_status     ON Reports(status);
