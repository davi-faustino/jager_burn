# 🎨 Frontend - Jager Burn Calculator

Modern web interface built with Next.js to visualize Jager token burn data.

## 📋 What Does This Frontend Do?

This is the "face" of the application. It:
- 📊 Displays interactive daily burn charts
- 💰 Shows real-time tokenomics metrics
- 📈 Presents future burn projections
- 🎯 Offers comparative summaries (yesterday vs today)
- 📱 Responsive interface that works on desktop and mobile

## 🚀 How to Run (Step by Step)

### Step 1: Install Node.js

If you don't have Node.js installed yet:
1. Go to [nodejs.org](https://nodejs.org/)
2. Download the LTS version (recommended)
3. Run the installer and follow the instructions
4. To verify it installed correctly, open the terminal and type:
   ```bash
   node --version
   npm --version
   ```

### Step 2: Navigate to the frontend folder

Open the terminal (Command Prompt or PowerShell on Windows) and navigate to the frontend folder:

```bash
cd C:\projetos\pessoal\jager_burn\frontend
```

### Step 3: Install dependencies

Run the command to install all required packages:

```bash
npm install
```

This may take a few minutes. The command will install:
- Next.js (React framework)
- React (UI library)
- TypeScript (static typing)
- TailwindCSS (styling)
- Recharts (charts)
- And other dependencies

### Step 4: Configure backend connection

1. Copy the example file:
   ```bash
   copy .env.example .env.local
   ```

2. Open the `.env.local` file in a text editor

3. **Configure the backend URL:**
   
   If you're running the backend **locally** (on your machine):
   ```bash
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
   
   If you're using a backend **in production**:
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://jager-burn-backend.fly.dev
   ```

⚠️ **Important:** The backend needs to be running for the frontend to work! See instructions at [`../backend/README.md`](../backend/README.md)

### Step 5: Run the development server

With everything configured, start the server:

```bash
npm run dev
```

If everything went well, you'll see something like:
```
▲ Next.js 14.2.0
- Local:        http://localhost:3000
- Ready in 2.5s
```

🎉 **Done!** Your frontend is running at `http://localhost:3000`

### Step 6: Open in browser

Open your favorite browser and go to:
```
http://localhost:3000
```

You'll see the dashboard with:
- Tokenomics cards (supply, burn, price)
- Burn summary (yesterday vs today)
- Projection calculator
- Daily burn chart

## 🎯 Interface Features

### 1. Tokenomics Cards
Displays in real-time:
- **Max Supply**: Maximum token supply
- **Total Burned**: Total amount burned
- **Burn %**: Percentage of supply burned
- **Remaining Supply**: Remaining supply in circulation
- **Current Price**: Current token price

### 2. Summary Cards
Compares burn data:
- **Yesterday**: Total burned on previous day
- **Today**: Total burned on current day
- **Variation**: Percentage difference between days

### 3. Projection Calculator
Allows calculating future projections:
- **Data Window**: How many days to use for calculation (7, 14, 30, 60, 90, 180, 365)
- **Horizon**: How many days to project into the future (30, 60, 90, 180, 365, 730, 1095, 1825, 3650)
- **Model**: Type of calculation (Simple Mean or Linear Regression)

### 4. Burn Chart
Interactive chart showing:
- Daily burn over time
- Period selection (7, 14, 30, 60, 90, 180, 365 days)
- Hover to see exact values

## 💡 Tips and Troubleshooting

### Error: "Failed to fetch" or data doesn't appear
- **Check if the backend is running** at `http://localhost:8000`
- Test by accessing `http://localhost:8000/health` in the browser
- Confirm the URL in `.env.local` is correct

### Error: "Cannot find module"
- Run `npm install` again
- Make sure you're in the `frontend` folder

### Error: "Port 3000 is already in use"
- Another application is using port 3000
- Stop the other application or use another port:
  ```bash
  npm run dev -- -p 3001
  ```

### How to stop the server
- Press `CTRL+C` in the terminal where the server is running

### Clear cache and reinstall
If something isn't working:
```bash
# Remove node_modules and cache
rmdir /s /q node_modules
rmdir /s /q .next
del package-lock.json

# Reinstall
npm install
npm run dev
```

## 🔧 Available Scripts

- **`npm run dev`**: Starts the development server
- **`npm run build`**: Creates an optimized production build
- **`npm start`**: Runs the production version (after build)
- **`npm run lint`**: Checks for code issues

## 📁 Project Structure

```
frontend/
├── app/
│   ├── components/        # React components
│   │   ├── TokenomicsCards.tsx
│   │   ├── SummaryCards.tsx
│   │   ├── ProjectionCalculator.tsx
│   │   └── BurnChart.tsx
│   ├── lib/              # Utilities
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Main layout
│   └── page.tsx          # Home page
├── .env.local            # Your settings (DO NOT COMMIT)
├── .env.example          # Configuration example
├── package.json          # Dependencies and scripts
├── tailwind.config.ts    # TailwindCSS configuration
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## 🎨 Technologies Used

- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: JavaScript with static typing
- **TailwindCSS**: Utility-first CSS framework for styling
- **Recharts**: Library for interactive charts
- **Vercel Analytics**: Application usage analytics

## 🌐 Production Deployment

To deploy the application:

1. **Production build:**
   ```bash
   npm run build
   ```

2. **Test locally:**
   ```bash
   npm start
   ```

3. **Deploy on Vercel (recommended):**
   - Create an account at [vercel.com](https://vercel.com)
   - Connect your GitHub repository
   - Configure the environment variable `NEXT_PUBLIC_API_BASE_URL`
   - Automatic deployment!

## 🆘 Need Help?

- Check if the backend is running and accessible
- Open the browser console (F12) to see errors
- Confirm the `.env.local` file is configured correctly
- Review the logs in the terminal where the server is running

## 📝 Important Notes

- The frontend **depends** on the backend to work
- Always start the backend before the frontend
- Settings in `.env.local` are not committed to Git (for security)
- For development, use `npm run dev` (automatic hot reload)

---

**Built with Next.js and ❤️**