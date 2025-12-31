module.exports = {
    apps: [{
        name: "honolulu",
        script: "npm",
        args: "start",
        cwd: "/root/honolulu",
        exp_backoff_restart_delay: 100,
        env: {
            NODE_ENV: "production",
            PORT: 3006
        }
    }]
}
