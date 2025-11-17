# VPS Deployment Guide

This guide will help you deploy the Psychology Support Bot on a VPS.

## Prerequisites

- A VPS with Ubuntu/Debian (recommended)
- SSH access to your VPS
- PostgreSQL installed on VPS
- Python 3.8 or higher
- A Telegram bot token from @BotFather

## Step 1: Prepare Your VPS

SSH into your VPS:

```bash
ssh user@your-vps-ip
```

Update system packages:

```bash
sudo apt update
sudo apt upgrade -y
```

Install required packages:

```bash
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git
```

## Step 2: Set Up PostgreSQL

Switch to postgres user:

```bash
sudo -u postgres psql
```

Create database and user:

```sql
CREATE DATABASE psy_bot;
CREATE USER psy_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE psy_bot TO psy_user;
\q
```

## Step 3: Upload Your Bot Files

Option 1: Using Git (recommended)

```bash
cd /home/your-user
git clone your-repository-url psy_bot
cd psy_bot
```

Option 2: Using SCP from your local machine

```bash
# From your local machine
scp -r /home/based/projects/psy user@your-vps-ip:/home/user/psy_bot
```

## Step 4: Configure Environment

Navigate to bot directory:

```bash
cd /home/user/psy_bot
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create and edit `.env` file:

```bash
nano .env
```

Add your configuration:

```
BOT_TOKEN=your_bot_token_here
PSYCHOLOGIST_ID=psychologist_telegram_id_here
DATABASE_URL=postgresql://psy_user:your_secure_password@localhost:5432/psy_bot
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 5: Test the Bot

Run the bot manually to test:

```bash
source venv/bin/activate
python main.py
```

Press Ctrl+C to stop when testing is complete.

## Step 6: Set Up Systemd Service (Keep Bot Running)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/psy-bot.service
```

Add the following content (replace paths with your actual paths):

```ini
[Unit]
Description=University Psychology Support Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/psy_bot
Environment="PATH=/home/your-user/psy_bot/venv/bin"
ExecStart=/home/your-user/psy_bot/venv/bin/python /home/your-user/psy_bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable psy-bot
sudo systemctl start psy-bot
```

Check status:

```bash
sudo systemctl status psy-bot
```

## Step 7: Manage the Bot Service

### View logs:

```bash
sudo journalctl -u psy-bot -f
```

### Restart bot:

```bash
sudo systemctl restart psy-bot
```

### Stop bot:

```bash
sudo systemctl stop psy-bot
```

### Start bot:

```bash
sudo systemctl start psy-bot
```

## Step 8: Set Up Firewall (Optional but Recommended)

Allow SSH and PostgreSQL:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

## Updating the Bot

When you need to update the bot:

```bash
cd /home/user/psy_bot
git pull  # If using git
sudo systemctl restart psy-bot
```

## Troubleshooting

### Bot not starting:

Check logs:
```bash
sudo journalctl -u psy-bot -n 50
```

### Database connection issues:

Test PostgreSQL connection:
```bash
psql -U psy_user -d psy_bot -h localhost
```

### Permission issues:

Ensure the user has proper permissions:
```bash
sudo chown -R your-user:your-user /home/user/psy_bot
```

## Security Recommendations

1. **Change default PostgreSQL password** to something strong
2. **Use SSH keys** instead of passwords for VPS access
3. **Keep your `.env` file secure** - never commit to git
4. **Regular backups** of your database:

```bash
pg_dump -U psy_user psy_bot > backup_$(date +%Y%m%d).sql
```

5. **Update system regularly**:

```bash
sudo apt update && sudo apt upgrade -y
```

## Getting Telegram IDs

### Get Psychologist ID:

1. Psychologist should send a message to [@userinfobot](https://t.me/userinfobot)
2. The bot will return their Telegram ID
3. Use this ID in the `.env` file

### Get Bot Token:

1. Open [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the instructions
4. Copy the token to your `.env` file

## Monitoring

To ensure the bot is running 24/7, you can set up a simple monitoring script:

```bash
nano /home/user/check_bot.sh
```

Add:

```bash
#!/bin/bash
if ! systemctl is-active --quiet psy-bot; then
    systemctl start psy-bot
    echo "Bot was down, restarted at $(date)" >> /var/log/psy-bot-monitor.log
fi
```

Make executable:

```bash
chmod +x /home/user/check_bot.sh
```

Add to crontab (runs every 5 minutes):

```bash
crontab -e
```

Add line:

```
*/5 * * * * /home/user/check_bot.sh
```

## Support

If you encounter issues during deployment, check:
1. System logs: `sudo journalctl -xe`
2. Bot logs: `sudo journalctl -u psy-bot -f`
3. PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
