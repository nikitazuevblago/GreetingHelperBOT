# Use Python 3.11 slim version as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary Python files
COPY sessions/5303965494.session ./sessions/
COPY .env .
COPY db_interaction.py .
COPY custom_logging.py .
COPY user_account.py .
COPY bot.py .

# Run the bot.py script
CMD ["python", "bot.py"]

#docker build -t greetinghelperbot .