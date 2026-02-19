module.exports = {
  apps: [{
    name: 'personal-ai-employee',
    script: 'src/filesystem_watcher.py',
    interpreter: 'python',
    cwd: './',
    watch: false,
    env: {
      NODE_ENV: 'development',
      DRY_RUN: 'true'
    },
    env_production: {
      NODE_ENV: 'production',
      DRY_RUN: 'false'
    }
  }]
};