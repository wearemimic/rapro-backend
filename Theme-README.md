
# Retirement Advisor Pro - Frontend

This project integrates the Front Dashboard Bootstrap theme into a Vue + Vite application for the Retirement Advisor Pro platform.

## Directory Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── assets/
│   │   ├── css/
│   │   ├── fonts/
│   │   ├── img/
│   │   ├── js/
│   ├── components/
│   ├── views/
│   │   ├── Login.vue
│   │   └── Dashboard.vue
│   ├── router/
│   │   └── index.js
│   ├── App.vue
│   └── main.js
├── package.json
├── vite.config.js
└── README.md
```

## Theme Integration Plan

### 1. Bootstrap Theme Source
- Imported from `dist.zip` from the Front Dashboard Bootstrap theme.
- Key files: `authentication-signup-basic.html` and `dashboard-default-light-sidebar.html`.

### 2. Login Page Integration
- File: `authentication-signup-basic.html`
- Target Vue Component: `src/views/Login.vue`
- Integrate relevant CSS, images, JS, and HTML from the theme into Vue SFC format.

### 3. Dashboard Page Integration
- File: `dashboard-default-light-sidebar.html`
- Target Vue Component: `src/views/Dashboard.vue`
- Includes navigation sidebar, header, and sample cards.

### 4. Static Assets
- CSS, JS, images, and fonts copied to `src/assets/`.

### 5. Routing Setup
- Vue Router configured in `src/router/index.js` to support `/login` and `/dashboard` paths.

### 6. Build & Run
```bash
cd frontend
npm install
npm run dev
```

Access the site at: [http://localhost:3000](http://localhost:3000)
