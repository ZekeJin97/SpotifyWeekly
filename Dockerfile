# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory inside the container
WORKDIR /var/task

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code into the container
COPY SpotifyLambda.py .

# Set the command to run the function handler
CMD ["SpotifyLambda.lambda_handler"]
