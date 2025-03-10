# Use an official Python 3.9 slim image
FROM python:3.9-slim

# Install ffmpeg (required for merging video and audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY telegram_media_downloader_bot.py ./

# Command to run the bot
CMD ["python3", "telegram_media_downloader_bot.py"]
