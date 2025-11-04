# Railway Deployment Guide for DevOps Django App

## 🚂 Quick Railway Deployment

Railway is the fastest way to deploy your Django app with built-in PostgreSQL and zero configuration.

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Your code pushed to GitHub

### 🚀 Deploy in 5 Minutes

#### Step 1: Prepare Your Code
```bash
# Make sure you're in the project directory
cd devops

# Add and commit all files
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

#### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `devops` repository
5. Railway will automatically detect it's a Django app

#### Step 3: Add Database
1. In your Railway project dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway automatically connects it to your app

#### Step 4: Set Environment Variables
In Railway dashboard, go to your app service → Variables tab:

```bash
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.up.railway.app
```

#### Step 5: Generate Domain
- Go to Settings tab in your app service
- Click "Generate Domain" 
- Your app will be live at: `https://your-app-name.up.railway.app`

#### Step 6: Create Admin User
In Railway dashboard → your app → Deploy logs, click the console icon:
```bash
python manage.py createsuperuser
```

### ✅ That's It!
Your app is now live with:
- ✅ Automatic HTTPS
- ✅ PostgreSQL database
- ✅ Auto-deployments on git push
- ✅ Built-in monitoring
- ✅ Scalable infrastructure

## 🔧 Railway-Specific Features

### Automatic Environment Variables
Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port
- `RAILWAY_ENVIRONMENT` - Current environment

### Custom Domain (Optional)
1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records as shown
4. Update `ALLOWED_HOSTS` in environment variables

### Monitoring
- Built-in metrics in Railway dashboard
- Real-time logs and deployment status
- Resource usage tracking

## 💰 Pricing
- **Hobby Plan**: $5/month (includes everything you need)
- **Pro Plan**: $8/month (more resources)
- Free tier available for testing

## 🔄 Development Workflow

### Local Development
```bash
# Use SQLite locally
DEBUG=True python manage.py runserver

# Or connect to Railway database locally
# Copy DATABASE_URL from Railway dashboard
DATABASE_URL="postgresql://..." python manage.py runserver
```

### Deployment
```bash
# Just push to GitHub - Railway auto-deploys
git add .
git commit -m "Update feature"
git push origin main
```

## 🛠️ Advanced Configuration

### Custom Build Command
If you need custom build steps, update `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn devops.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
```

### Environment-Specific Settings
Railway automatically sets production-optimized environment variables.

## 🔍 Troubleshooting

### Build Failures
- Check deploy logs in Railway dashboard
- Ensure `requirements.txt` is in root directory
- Verify all dependencies are listed

### Database Issues
- Database URL is automatically provided
- Check Variables tab for `DATABASE_URL`
- Use Railway's built-in PostgreSQL

### Static Files
- WhiteNoise handles static files automatically
- Files are collected during deployment
- No additional configuration needed

## 📊 Monitoring Your App

### Railway Dashboard
- Real-time metrics
- Deploy history
- Resource usage
- Custom alerts

### Application Logs
```bash
# View logs in Railway dashboard
# Or use Railway CLI
railway logs
```

## 🚀 Going to Production

### Checklist
- ✅ Custom domain configured
- ✅ Environment variables set
- ✅ Database backups enabled (automatic)
- ✅ Error tracking setup (optional)
- ✅ Admin user created

### Scaling
Railway automatically scales based on traffic. For high-traffic apps:
1. Upgrade to Pro plan
2. Enable horizontal scaling
3. Add Redis for caching (optional)

## 🎯 Why Railway?

- **Zero Config**: Automatic Django detection
- **Built-in Database**: PostgreSQL included
- **Git Integration**: Deploy on push
- **Modern Stack**: Latest infrastructure
- **Great DX**: Excellent developer experience
- **Fair Pricing**: Pay for what you use

Your Django app is now production-ready on Railway! 🎉