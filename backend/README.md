# 🔥 Backend - Jager Burn Calculator

API built with FastAPI to monitor and calculate Jager token burns.

## 📋 What Does This Backend Do?

This is the "brain" of the application. It:
- 🔍 Fetches blockchain data through the Moralis API
- 💾 Stores data in local cache to save credits
- 📊 Calculates daily burn statistics
- 📈 Generates future projections using mathematical models
- 🌐 Provides a REST API for the frontend to consume

## 🚀 How to Run (Step by Step)

### Step 1: Install Python

If you don't have Python installed yet:
1. Go to [python.org](https://www.python.org/downloads/)
2. Download version 3.8 or higher
3. During installation, **check the "Add Python to PATH" option**
4. To verify it installed correctly, open the terminal and type:
   ```bash
   python --version
   ```

### Step 2: Navigate to the backend folder

Open the terminal (Command Prompt or PowerShell on Windows) and navigate to the backend folder:

```bash
cd C:\projetos\pessoal\jager_burn\backend
```

### Step 3: Create a virtual environment

The virtual environment keeps project dependencies isolated. Run:

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

You'll know it worked when `(.venv)` appears at the beginning of the terminal line.

### Step 4: Install dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (server)
- HTTPX (HTTP client)
- Pydantic (data validation)
- Python-dotenv (environment variable management)

### Step 5: Configure environment variables

1. Copy the example file:
   ```bash
   copy .env.example .env
   ```

2. Open the `.env` file in a text editor

3. **Configure your Moralis key:**
   - Go to [moralis.io](https://moralis.io) and create a free account
   - Go to "API Keys" and copy your key
   - Paste it in the `.env` file on the line `MORALIS_API_KEY="YOUR_KEY_HERE"`

4. **Review other settings** (usually don't need to be changed):
   - `TOKEN_ADDRESS`: Jager token contract address
   - `MAX_SUPPLY_TOKENS`: Token max supply
   - `CACHE_DB_PATH`: Where cache will be stored

### Step 6: Run the server

With everything configured, start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

If everything went well, you'll see something like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

🎉 **Done!** Your backend is running at `http://localhost:8000`

### Step 7: Test if it's working

Open your browser and go to:
- `http://localhost:8000` - Home page
- `http://localhost:8000/docs` - Interactive API documentation
- `http://localhost:8000/health` - Health check

## 📚 Available Endpoints

Go to `http://localhost:8000/docs` to see the complete interactive documentation. The main endpoints are:

- **GET /health** - Check if the API is working
- **GET /token/meta** - Basic token information
- **GET /token/metrics** - Complete metrics (supply, burn, price)
- **GET /burn/summary** - Burn summary (yesterday vs today)
- **GET /burn/series** - Historical daily burn series
- **GET /burn/projection** - Future burn projections

## 🔄 Filling Historical Data (Backfill)

📅 **Note:** The `cache.sqlite3` database included in the project is already updated until **01/30/2026**.

If you cloned the repository and already have the `cache.sqlite3` file, you **don't need** to run the initial backfill. The history is already filled!

### When to run the backfill?

Run the backfill only if:
- You don't have the `cache.sqlite3` file
- You want to fill data from a date before 04/28/2025
- You accidentally deleted the cache

### How to run the backfill

Run **only once**:

```bash
python -m app.backfill --start 2025-04-28
```

Replace `2025-04-28` with the initial date you want to start the history.

⚠️ **Warning:** This command consumes Moralis API credits. Run only once!

## 💡 Tips and Troubleshooting

### Error: "MORALIS_API_KEY not defined"
- Check if you created the `.env` file
- Confirm you put your Moralis key correctly

### Error: "ModuleNotFoundError"
- Make sure the virtual environment is activated (`.venv` should appear in the terminal)
- Run `pip install -r requirements.txt` again

### Error: "MISSING_HISTORICAL_CACHE"
- You need to run the backfill (Step 7 above)
- Or copy an existing `cache.sqlite3` file to the backend folder

### How to stop the server
- Press `CTRL+C` in the terminal where the server is running

### How to deactivate the virtual environment
```bash
deactivate
```

## 🔒 Saving Moralis Credits

The backend was designed to save your free Moralis credits:

- **Local Cache**: Data is stored in SQLite and reused
- **Configurable TTL**: You define how long data stays in cache
- **Automatic Protection**: By default, historical days are not fetched automatically
- **Manual Backfill**: You control when to fetch historical data

### Cache Settings in `.env`

```bash
CACHE_TTL_SECONDS="300"  # 5-minute cache for general data
SERIES_CACHE_TTL_SECONDS="300"  # 5-minute cache for series
ALLOW_FETCH_MISSING_HISTORICAL_DAYS="false"  # Don't fetch history automatically
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py           # Main application and routes
│   ├── config.py         # Configuration
│   ├── db.py             # SQLite cache management
│   ├── moralis.py        # Moralis API client
│   ├── burn_service.py   # Burn calculation logic
│   ├── backfill.py       # Historical backfill script
│   └── utils.py          # Helper functions
├── .env                  # Your settings (DO NOT COMMIT)
├── .env.example          # Configuration example
├── requirements.txt      # Python dependencies
├── cache.sqlite3         # Cache database (auto-generated)
└── README.md            # This file
```

## 🚀 Production Deployment

The project comes pre-configured for easy deployment using Docker and Fly.io.

### Option 1: Deploy on Fly.io (Recommended - Free)

Fly.io offers a generous free tier and is very easy to use.

#### Step 1: Install Fly CLI

**Windows:**
```bash
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Linux/Mac:**
```bash
curl -L https://fly.io/install.sh | sh
```

#### Step 2: Create account and login

```bash
fly auth signup
# or if you already have an account:
fly auth login
```

#### Step 3: Configure the application

The `fly.toml` file is already configured! You just need to create the application:

```bash
fly launch
```

When asked:
- **Would you like to copy its configuration to the new app?** → Yes
- **Choose an app name** → Leave blank to auto-generate or choose a name
- **Choose a region** → Choose the closest region (e.g., gru for São Paulo)
- **Would you like to set up a PostgreSQL database?** → No
- **Would you like to deploy now?** → No (we'll configure variables first)

#### Step 4: Configure environment variables

Configure your secret environment variables:

```bash
fly secrets set MORALIS_API_KEY="your_key_here"
fly secrets set TOKEN_ADDRESS="0x74836cC0E821A6bE18e407E6388E430B689C66e9"
fly secrets set MAX_SUPPLY_TOKENS="14600000000000000"
fly secrets set TOKEN_DECIMALS="18"
```

Optionally, configure CORS to allow your frontend:
```bash
fly secrets set CORS_ORIGINS="https://your-frontend.vercel.app,http://localhost:3000"
```

#### Step 5: Deploy

```bash
fly deploy
```

🎉 Done! Your API will be available at `https://your-app.fly.dev`

#### Useful Fly.io commands

```bash
fly status              # View application status
fly logs                # View logs in real-time
fly ssh console         # Access application console
fly secrets list        # List environment variables
fly scale show          # View allocated resources
fly apps destroy        # Delete the application
```

#### Fill cache in production

After the first deploy, you need to fill the historical cache:

```bash
fly ssh console
python -m app.backfill --start 2025-04-28
exit
```

### Option 2: Deploy with Docker (Any Platform)

The `Dockerfile` allows deployment on any platform that supports containers.

#### Build the image

```bash
docker build -t jager-burn-backend .
```

#### Run locally with Docker

```bash
docker run -p 8080:8080 \
  -e MORALIS_API_KEY="your_key" \
  -e TOKEN_ADDRESS="0x74836cC0E821A6bE18e407E6388E430B689C66e9" \
  -e MAX_SUPPLY_TOKENS="14600000000000000" \
  jager-burn-backend
```

#### Deploy on other platforms

The Dockerfile works on:
- **Railway**: `railway up`
- **Render**: Connect your repository and configure variables
- **Google Cloud Run**: `gcloud run deploy`
- **AWS ECS/Fargate**: Use the Dockerfile to create the task
- **Azure Container Apps**: `az containerapp up`

### 💾 Cache Persistence in Production

⚠️ **Important**: Fly.io and most container platforms **do not persist files** between deploys.

To keep the SQLite cache between deploys, you have two options:

#### Option A: Use Fly.io Volumes (Recommended)

```bash
# Create a persistent volume
fly volumes create cache_data --size 1

# Uncomment the [mounts] section in fly.toml:
# [mounts]
#   source = "cache_data"
#   destination = "/app/data"

# Update CACHE_DB_PATH in fly.toml to:
fly secrets set CACHE_DB_PATH="/app/data/cache.sqlite3"

# Deploy again
fly deploy
```

#### Option B: Accept that cache will be recreated

If you don't mind recreating the cache on each deploy (consumes Moralis credits):
- Keep `ALLOW_FETCH_MISSING_HISTORICAL_DAYS=false`
- After each deploy, run the backfill manually via SSH
- Today's cache will be recreated automatically

### 🔒 Production Security

Before deploying, review:

1. **Never commit the `.env` file** with your keys
2. **Use secrets/environment variables** from the platform
3. **Configure CORS** properly to allow only your frontend
4. **Monitor credit usage** from Moralis
5. **Consider rate limiting** if the API is public

## 🆘 Need Help?

- Check the interactive documentation at `http://localhost:8000/docs`
- Review the logs in the terminal where the server is running
- Confirm all environment variables are configured correctly
- For Fly.io deployment issues: `fly logs` and [community.fly.io](https://community.fly.io)

---

**Built with FastAPI and ❤️**
