# Serving uploaded images on AWS Ubuntu (dev.admin-montanapharmacy.com)

Product images are stored in the `media/` folder and must be served at `/media/`.

## Nginx Configuration

Add this to your Nginx config (e.g. `/etc/nginx/sites-available/your-site`):

```nginx
server {
    listen 443 ssl;
    server_name dev.admin-montanapharmacy.com;

    # ... SSL config ...

    # Serve media files
    location /media/ {
        alias /path/to/your/project/media/;
    }

    # Serve static files
    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    # Proxy to Django/Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

After updating, reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Result

Uploaded images will be available at:

- `https://dev.admin-montanapharmacy.com/media/products/xxx.jpg`
- `https://dev.admin-montanapharmacy.com/media/brands/xxx.jpg`
- etc.
