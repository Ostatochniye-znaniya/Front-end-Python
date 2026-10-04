"use client";

import { useEffect, useState } from 'react';

export default function Home() {
  const [isDark, setIsDark] = useState(false);

  // Проверяем системную тему
  useEffect(() => {
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDark(darkModeQuery.matches);

    // Слушаем изменения системной темы
    const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
    darkModeQuery.addEventListener('change', handler);
    return () => darkModeQuery.removeEventListener('change', handler);
  }, []);

  return (
    <div>
      <h1>Текущая тема: {isDark ? '🌙 Тёмная' : '☀️ Светлая'}</h1>
      <p>Измените системную тему, чтобы увидеть изменения</p>
    </div>
  );
}