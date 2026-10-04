"use client";

import Navbar from "@/components/navbar/Navbar";

export default function Home() {
  return (
    <div>
        <Navbar
            title="Проверка остаточных знаний"
            linkOptions={[
                { label: "Преподаватель", href: "/csh/teacher/main" },
                { label: "ЛПР", href: "/csh/lpr/main" },
                { label: "Заведующего кафедрой", href: "/csh/hod/main" }
            ]}
            name="Иван"
            surname="Иванов"
            lastname="Иванович"
        />
    </div>
  );
}
