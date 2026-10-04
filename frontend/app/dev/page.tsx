"use client";

import Button from "@/components/button/Button";
import CheckBox from "@/components/checkbox/CheckBox";
import Alert from "@/components/alert/Alert";
import Input from "@/components/input/Input";
import Search from "@/components/search/Search";
import Table from "@/components/table/Table";
import Dropdown from "@/components/dropdown/Dropdown";
import Pagination from "@/components/pagination/Pagination";

import { useState } from "react";

const users = [
  {
    id: 1,
    name: 'Иван Иванов',
    age: 25,
    active: true,
    role: 'Администратор',
    email: 'ivan@mail.ru',
    registered: '2023-01-15'
  },
  {
    id: 2,
    name: 'Петр Петров',
    age: 30,
    active: false,
    role: 'Пользователь',
    email: 'petr@mail.ru',
    registered: '2023-03-20'
  },
  {
    id: 3,
    name: 'Анна Смирнова',
    age: 28,
    active: true,
    role: 'Модератор',
    email: 'anna@mail.ru',
    registered: '2023-02-10'
  },
  {
    id: 4,
    name: 'Елена Козлова',
    age: 35,
    active: true,
    role: 'Администратор',
    email: 'elena@mail.ru',
    registered: '2022-11-05'
  },
  {
    id: 5,
    name: 'Дмитрий Новиков',
    age: 22,
    active: false,
    role: 'Пользователь',
    email: 'dima@mail.ru',
    registered: '2023-05-30'
  },
  {
    id: 6,
    name: 'Ольга Морозова',
    age: 27,
    active: true,
    role: 'Модератор',
    email: 'olga@mail.ru',
    registered: '2023-04-12'
  }
];

const cities = [
    { value: 'msk', label: 'Москва' },
    { value: 'spb', label: 'Санкт-Петербург' },
    { value: 'kazan', label: 'Казань' },
    { value: 'novosib', label: 'Новосибирск' },
    { value: 'ekb', label: 'Екатеринбург' }
  ];

  const roles = [
    { value: 'admin', label: 'Администратор' },
    { value: 'user', label: 'Пользователь' },
    { value: 'moder', label: 'Модератор' },
    { value: 'guest', label: 'Гость' }
  ];

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [inputBigValue, setInputBigValue] = useState('');
  const [searchValue, setSearchValue] = useState('');
  const [searchBigValue, setSearchBigValue] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = 20;

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Здесь можно добавить логику загрузки данных для новой страницы
    console.log('Переход на страницу:', page);
  };

  return (
    <div>
      <p className="title">Московский Политехнический Университет - Остаточные знания</p>
      <p className="text">Это тестовая страница для проверки компонентов</p>
      <p className="title">Кнопки</p>
      <div className="flex">
        <Button title="Кнопка 1" color="btn-blue" onClick={() => alert("Кнопка 1 нажата")} />
        <div style={{ marginLeft: '10px' }}></div>
        <Button title="Кнопка 2" color="btn-red" onClick={() => alert("Кнопка 2 нажата")} />
        <div style={{ marginLeft: '10px' }}></div>
        <Button title="Кнопка 3" color="btn-orange" onClick={() => alert("Кнопка 3 нажата")} />
        <div style={{ marginLeft: '10px' }}></div>
        <Button title="Кнопка 4" color="btn-green" onClick={() => alert("Кнопка 4 нажата")} />
        <div style={{ marginLeft: '10px' }}></div>
        <Button title="Кнопка 5" color="btn-purple" onClick={() => alert("Кнопка 5 нажата")} />
      </div>
      <p className="title">Чекбоксы</p>
      <div className="flex">
        <CheckBox text="Чек бокс с галкой" type="blue" />
        <CheckBox text="Чек бокс с крестиком" type="red" />
      </div>
      <p className="title">Поиск</p>
      <Search hint="Поиск" value={searchValue} onChange={(value) => setSearchValue(value)} size="small" />
      <p className="title">Большой поиск</p>
      <Search hint="Введите сюда" value={searchBigValue} onChange={(value) => setSearchBigValue(value)} size="large" />
      <p className="title">Выпадающий список</p>
      <div style={{ display: 'flex', gap: '20px' }}>
      <Dropdown
          options={cities}
          value={selectedCity}
          onChange={setSelectedCity}
          placeholder="Выберите город"
          label="Город"
        />

        <Dropdown
          options={roles}
          value={selectedRole}
          onChange={setSelectedRole}
          placeholder="Выберите роль"
          label="Роль"
        />
      </div>
      <p className="title">Ввод</p>
      <Input hint="Введите текст..." value={inputValue} onChange={(value) => setInputValue(value)} />
      <p className="title">Большой ввод</p>
      <Input hint="Описание" value={inputBigValue} onChange={(value) => setInputBigValue(value)} multiline rows={5} />
      <p className="title">Уведомления</p>
      <Alert type="success" title="Успешная операция" text="Текст" />
      <div style={{
        height: '20px'
      }}></div>
      <Alert type="error" title="Произошла ошибка" text="Текст" />
      <div style={{
        height: '20px'
      }}></div>
      <Alert type="warning" title="Предупреждение" text="Текст" />
      <div style={{
        height: '20px'
      }}></div>
      <Alert type="info" title="Информация" text="Текст" />
      <p className="title">Таблица</p>
      <Table
        columns={[
          {
            header: 'Имя',
            accessor: 'name',
            sortFn: (a, b) => a.name.localeCompare(b.name)
          },
          {
            header: 'Возраст',
            accessor: 'age',
            sortFn: (a, b) => a.age - b.age
          },
          {
            header: 'Роль',
            accessor: 'role',
            sortFn: (a, b) => a.role.localeCompare(b.role)
          },
          {
            header: 'Email',
            accessor: 'email'
          },
          {
            header: 'Статус',
            accessor: (row) => (
              <span style={{ color: row.active ? 'green' : 'red' }}>
                {row.active ? 'Активен' : 'Неактивен'}
              </span>
            ),
            sortFn: (a, b) => (a.active === b.active ? 0 : a.active ? -1 : 1)
          }
        ]}
        data={users}
      />
      <p className="title">Пагинация</p>
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
        siblingCount={2}
        showFirstLast={true}
      />
    </div>
  );
}
