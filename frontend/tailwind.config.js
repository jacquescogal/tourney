/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors:{
        'gt-white': "#fbfbfb",
        'gt-off-white': "#f0f4f6",
        'gt-blue':'#275b85',
        'text-pop':'#344054',
        'text-norm':'#656d7c',
        'test-green':'#00A300'
      },
      spacing: {

        'sub-header': '40px',
        'header': '80px',
        'header-3/4': '60px',
        'header-1/2': '40px',
        'header-1/4': '20px',
        'screen-less-header': 'calc(100vh - 80px - 40px)',
        'article-wide': '700px',
        'article-wide-1/4': '175px',
        'article-wide-1/2': '350px',
        'article-wide-3/4': '625px'
      },
    },
  },
  plugins: [],
}

