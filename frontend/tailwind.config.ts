import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        soil: {
          50: '#f7f6f1',
          100: '#ece7dc',
          200: '#d8cfbd',
          300: '#c1b498',
          400: '#9f9275',
          500: '#796b52',
          600: '#5c503e',
          700: '#43392d',
          800: '#2b241d',
          900: '#191511',
        },
        leaf: {
          50: '#eef9f0',
          100: '#dff4e3',
          200: '#c0e9ca',
          300: '#90d4a2',
          400: '#5dbb73',
          500: '#319255',
          600: '#277347',
          700: '#205b3b',
          800: '#18442d',
          900: '#102c1d',
        },
      },
      boxShadow: {
        soft: '0 18px 55px rgba(20, 28, 20, 0.10)',
      },
      backgroundImage: {
        'grain': 'radial-gradient(circle at 1px 1px, rgba(64, 82, 56, 0.10) 1px, transparent 0)',
      },
    },
  },
  plugins: [],
};

export default config;
