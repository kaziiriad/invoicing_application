# 🚀 Render Deployment Guide - Production Environment Variables

## 📋 Environment Variables to Set in Render Dashboard

### **Step 1: Access Render Environment Variables**
1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add these environment variables:

### **Core Django Settings**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `SECRET_KEY` | `your-super-secret-production-key-here` | Django secret key (generate new one) |
| `DEBUG` | `False` | Disable debug mode in production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com,your-custom-domain.com` | Allowed host domains |

### **Database Configuration**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:port/db` | PostgreSQL connection string |

**Note**: Render provides PostgreSQL addon. Get the connection string from:
- Render Dashboard → Database → Connection Details

### **CORS Configuration (Critical for Frontend)**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `CORS_ALLOWED_ORIGINS` | `https://your-vercel-app.vercel.app,https://your-custom-domain.com` | Frontend URLs |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Disable for security |

### **Security Settings**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `SECURE_SSL_REDIRECT` | `True` | Force HTTPS redirects |
| `SECURE_BROWSER_XSS_FILTER` | `True` | XSS protection |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Content type sniffing protection |
| `X_FRAME_OPTIONS` | `DENY` | Clickjacking protection |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS for 1 year |

### **JWT Token Settings**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `JWT_ACCESS_TOKEN_LIFETIME` | `60` | Access token lifetime (minutes) |
| `JWT_REFRESH_TOKEN_LIFETIME` | `1440` | Refresh token lifetime (minutes) |

## 🔧 Step-by-Step Render Configuration

### **1. Generate Production Secret Key**

```python
# Run this in Python to generate a new secret key
import secrets
print(secrets.token_urlsafe(50))
```

### **2. Get Your Render Service URLs**

Your backend will be available at:
- `https://your-service-name.onrender.com`

Update `ALLOWED_HOSTS` with this URL.

### **3. Update CORS for Vercel Frontend**

Get your Vercel URL and add to `CORS_ALLOWED_ORIGINS`:
- `https://your-vercel-app.vercel.app`

### **4. Database Setup**

If using Render PostgreSQL:
1. Create PostgreSQL service in Render
2. Copy the **External Database URL**
3. Set as `DATABASE_URL` environment variable

### **5. Static Files Configuration**

Render automatically serves static files if you set:
- `STATIC_URL=/static/`
- `STATIC_ROOT=/app/staticfiles/`

## 📱 Frontend Environment Variable

Update your Vercel environment variable:

| Variable Name | Value |
|---------------|-------|
| `VITE_API_URL` | `https://your-render-app.onrender.com/api` |

## 🔍 Testing the Deployment

### **1. Test Backend Health**
```bash
curl https://your-render-app.onrender.com/api/
```

### **2. Test API Endpoints**
```bash
# Test registration
curl -X POST https://your-render-app.onrender.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","password2":"test123"}'

# Test login
curl -X POST https://your-render-app.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

### **3. Test Frontend Integration**
- Visit your Vercel URL
- Try registration/login
- Check browser console for CORS errors

## 🚨 Common Issues & Solutions

### **CORS Errors**
- Ensure `CORS_ALLOWED_ORIGINS` includes your Vercel URL
- Check for trailing slashes in URLs
- Verify HTTPS vs HTTP

### **Database Connection Issues**
- Verify `DATABASE_URL` format
- Ensure PostgreSQL service is running
- Check firewall/network settings

### **Static Files Not Loading**
- Verify `STATIC_ROOT` and `STATIC_URL` settings
- Run `collectstatic` during build

### **SSL/HTTPS Issues**
- Render provides free SSL certificates
- Ensure `SECURE_SSL_REDIRECT=True`
- Update frontend to use HTTPS API URL

## 📝 Production Checklist

- [ ] ✅ `SECRET_KEY` generated and set
- [ ] ✅ `DEBUG=False`
- [ ] ✅ `ALLOWED_HOSTS` includes Render domain
- [ ] ✅ `DATABASE_URL` configured
- [ ] ✅ `CORS_ALLOWED_ORIGINS` includes Vercel URL
- [ ] ✅ Security headers enabled
- [ ] ✅ Frontend `VITE_API_URL` updated
- [ ] ✅ SSL/HTTPS working
- [ ] ✅ API endpoints tested
- [ ] ✅ Frontend-backend integration working

## 🔄 Deployment Commands

```bash
# If you need to redeploy after environment changes
git push origin main  # This triggers auto-deploy on Render

# Or manual deploy in Render dashboard
# Services → Your Service → Manual Deploy
```

## 📞 Support

If you encounter issues:
1. Check Render logs: Service → Logs
2. Check Vercel function logs
3. Browser developer console for frontend errors
4. Test API endpoints individually

## 🌟 Performance Tips

1. **Enable Render Disk Caching**
2. **Use Render PostgreSQL for better performance**
3. **Configure Redis for session storage (optional)**
4. **Monitor your service metrics in Render dashboard**

Your production setup should now be fully functional with secure environment variables!