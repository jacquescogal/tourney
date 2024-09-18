/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors:{
        'gt-white': "#ffffff",
        'gt-off-white': "#f0f4f6",
        'gt-blue':'#275b85',
        'text-pop':'#344054',
        'text-norm':'#656d7c',
        'test-green':'#00A300'
      },
      spacing: {
        'header': '80px',
        'screen-less-header': 'calc(100vh - 80px)',
        'article-wide': '700px',
        'article-wide-1/2': '350px'
      }
    },
  },
  plugins: [],
}

