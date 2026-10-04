"use client";

import React from 'react';

interface InputProps {
  hint: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
  rows?: number;
}

const Input: React.FC<InputProps> = ({
  hint,
  value,
  onChange,
  multiline = false,
  rows = 4
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  if (multiline) {
    return (
      <textarea
        className="input-field"
        placeholder={hint}
        value={value}
        onChange={handleChange}
        rows={rows}
      />
    );
  }

  return (
    <input
      className="input-field"
      type="text"
      placeholder={hint}
      value={value}
      onChange={handleChange}
    />
  );
}

export default Input;