"use client";

import React from 'react';

interface ButtonProps {
  title: string;
  color: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ title, color, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`btn ${color}`}
    >
      {title}
    </button>
  );
}

export default Button;