/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        sortify: {
          bg: '#040608',
          card: '#0a1019',
          blue: '#1682fc',
          blueDark: '#0f58cc',
          accent: '#46b5ff'
        }
      },
      boxShadow: {
        glow: '0 0 50px rgba(22, 130, 252, 0.35)'
      }
    }
  },
  plugins: []
}
