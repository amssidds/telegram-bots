```
docker build -t telegram_bot .
docker stop telegram_bot_container
docker rm telegram_bot_container
docker run -d --name telegram_bot_container --restart unless-stopped telegram_bot

```
