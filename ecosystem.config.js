module.exports = {
  apps: [
    {
      name: 'django-api',
      script: 'manage.py',
      args: 'runserver 0.0.0.0:8000',
      interpreter: 'env/bin/python3',
      cwd: '/home/subham/python/react-crud',
      watch: false
    }
  ]
}
