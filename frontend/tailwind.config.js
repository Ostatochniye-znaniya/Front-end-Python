// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'media',
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        secondary: {
          1: 'var(--secondary-1)',
          2: 'var(--secondary-2)',
          3: 'var(--secondary-3)',
          4: 'var(--secondary-4)',
          5: 'var(--secondary-5)',
          link: 'var(--secondary-link)',
          divider: 'var(--secondary-divider)',
          'link-hover': 'var(--secondary-link-hover)',
        },
        accent: {
          red: 'var(--accent-red)',
          'red-dark': 'var(--accent-red-dark)',
          'red-light': 'var(--accent-red-light)',
          orange: 'var(--accent-orange)',
          'orange-light': 'var(--accent-orange-light)',
          brown: 'var(--accent-brown)',
          green: 'var(--accent-green)',
          'green-dark': 'var(--accent-green-dark)',
          'green-light': 'var(--accent-green-light)',
          blue: 'var(--accent-blue)',
          'blue-dark': 'var(--accent-blue-dark)',
          'blue-light': 'var(--accent-blue-light)',
          purple: 'var(--accent-purple)',
          'purple-dark': 'var(--accent-purple-dark)',
          'purple-light': 'var(--accent-purple-light)',
        },
        bg: {
          main: 'var(--bg-main)',
          element: 'var(--bg-element)',
          inner: 'var(--bg-inner)',
        },
      },
      fontFamily: {
        sans: ['Montserrat', 'ui-sans-serif', 'system-ui'],
        mono: ['Geist Mono', 'ui-monospace', 'SFMono-Regular'],
      },
    },
  },
  safelist: [
    'px-4', 'py-2',
    'ring-2', 'ring-offset-2',
    'scale-95', 'shadow-md'
  ],
  plugins: [],
}