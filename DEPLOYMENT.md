# Deployment Guide for Kipenzi Django App with Supabase

This guide will help you deploy your Django application using Supabase as the database and a cloud hosting platform for the Django app.

## Prerequisites

1. A Supabase account (free at [supabase.com](https://supabase.com))
2. A GitHub account
3. A hosting platform account (Railway, Render, or Heroku recommended)

## Step 1: Set up Supabase Database

### 1.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `kipenzi-backend`
   - Database Password: Create a strong password
   - Region: Choose closest to your users
5. Click "Create new project"

### 1.2 Get Database Connection Details

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Copy the connection string from the "Connection string" section
3. It will look like: `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`

### 1.3 Set up Database Schema

You'll need to run your Django migrations on the Supabase database. You can do this locally first:

```bash
# Set the DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

## Step 2: Deploy Django App

### Option A: Deploy to Railway (Recommended)

1. **Sign up for Railway**: Go to [railway.app](https://railway.app) and sign up with GitHub

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your kipenzi repository

3. **Configure environment variables**:
   - Go to your project settings
   - Add the following environment variables:
     ```
     SECRET_KEY=your-generated-secret-key
     DEBUG=False
     ALLOWED_HOSTS=your-railway-domain.railway.app
     DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
     ```

4. **Deploy**: Railway will automatically deploy your app when you push to GitHub

### Option B: Deploy to Render

1. **Sign up for Render**: Go to [render.com](https://render.com) and sign up

2. **Create a new Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Name: `kipenzi-backend`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn kipenzi.wsgi:application`

3. **Set environment variables**:
   - Go to Environment section
   - Add the same environment variables as above

4. **Deploy**: Render will deploy your app

### Option C: Deploy to Heroku

1. **Install Heroku CLI** and sign up for Heroku

2. **Create Heroku app**:
   ```bash
   heroku create kipenzi-backend
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

## Step 3: Configure CORS and Security

1. **Update CORS settings** in `kipenzi/settings.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "https://your-frontend-domain.com",  # Add your frontend domain
   ]
   ```

2. **Update ALLOWED_HOSTS** with your deployment domain

## Step 4: Test Your Deployment

1. **Check your API endpoints**:
   - Visit `https://your-app-domain.com/admin/` to access Django admin
   - Test your API endpoints

2. **Monitor logs**:
   - Check your hosting platform's logs for any errors
   - Monitor Supabase dashboard for database activity

## Step 5: Set up Custom Domain (Optional)

1. **Add custom domain** in your hosting platform
2. **Update DNS records** to point to your app
3. **Update ALLOWED_HOSTS** and CORS settings

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `False` for production |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-domain.com,www.your-domain.com` |
| `DATABASE_URL` | Supabase PostgreSQL URL | `postgresql://postgres:...@db.xxx.supabase.co:5432/postgres` |

## Troubleshooting

### Common Issues:

1. **Database connection errors**:
   - Check your DATABASE_URL format
   - Ensure Supabase database is accessible
   - Verify network policies in Supabase

2. **Static files not loading**:
   - Run `python manage.py collectstatic` locally
   - Check STATIC_ROOT and STATICFILES_STORAGE settings

3. **CORS errors**:
   - Update CORS_ALLOWED_ORIGINS with your frontend domain
   - Check if your frontend is making requests to the correct backend URL

4. **Migration errors**:
   - Run migrations locally first: `python manage.py migrate`
   - Check for any custom SQL that might not work with PostgreSQL

## Security Best Practices

1. **Never commit sensitive data** to version control
2. **Use environment variables** for all secrets
3. **Enable SSL/HTTPS** in production
4. **Regularly update dependencies**
5. **Monitor your Supabase usage** to stay within free tier limits

## Cost Considerations

- **Supabase**: Free tier includes 500MB database, 2GB bandwidth
- **Railway**: Free tier available, then $5/month
- **Render**: Free tier available, then $7/month
- **Heroku**: No free tier, starts at $7/month

## Next Steps

1. Set up monitoring and logging
2. Configure automated backups
3. Set up CI/CD pipeline
4. Add performance monitoring
5. Set up staging environment

For more help, check out:
- [Supabase Documentation](https://supabase.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs) 