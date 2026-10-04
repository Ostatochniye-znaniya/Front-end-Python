"use client";

import React, { useState } from 'react';

interface Column<T = any> {
  header: React.ReactNode;
  accessor: keyof T | ((row: T) => React.ReactNode);
  sortFn?: (a: T, b: T) => number; // если есть - можно сортировать, если нет - нельзя
}

interface TableProps<T = any> {
  columns: Column<T>[];
  data: T[];
}

const Table = <T,>({ columns, data }: TableProps<T>) => {
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (colIndex: number) => {
    const column = columns[colIndex];
    // Сортируем только если есть sortFn
    if (!column.sortFn) return;

    if (sortColumn === colIndex) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(colIndex);
      setSortDirection('asc');
    }
  };

  const getSortedData = () => {
    if (sortColumn === null) return data;

    const column = columns[sortColumn];
    if (!column.sortFn) return data;

    return [...data].sort((a, b) => {
      return sortDirection === 'asc'
        ? column.sortFn!(a, b)
        : column.sortFn!(b, a);
    });
  };

  const sortedData = getSortedData();

  return (
    <table className="table-container">
      <thead>
        <tr>
          {columns.map((col, i) => (
            <th
              key={i}
              onClick={() => handleSort(i)}
              style={{ cursor: col.sortFn ? 'pointer' : 'default' }}
            >
              {col.header}
              {col.sortFn && sortColumn === i && (
                <span>{sortDirection === 'asc' ? ' ↑' : ' ↓'}</span>
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sortedData.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {columns.map((col, colIndex) => {
              const value = typeof col.accessor === 'function'
                ? col.accessor(row)
                : row[col.accessor] as React.ReactNode;

              return <td key={colIndex}>{value}</td>;
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default Table;