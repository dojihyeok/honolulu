module.exports = {
  apps: [
    {
      name: 'trydit',
      cwd: '/root/trydit',
      script: 'npm',
      args: 'start -- -p 3000',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'auditflow',
      cwd: '/root/auditflow/frontend',
      script: 'npm',
      args: 'start -- -p 3001',
      env: {
        NODE_ENV: 'production',
        PORT: 3001
      }
    },
    {
      name: 'portfolio',
      cwd: '/root/portfolio',
      script: 'npm',
      args: 'start -- -p 3002',
      env: {
        NODE_ENV: 'production',
        PORT: 3002
      }
    },
    {
      name: 'honolulu',
      cwd: '/root/honolulu',
      script: 'npm',
      args: 'start -- -p 3003',
      env: {
        NODE_ENV: 'production',
        PORT: 3003
      }
    }
  ]
};