# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Set working directory
WORKDIR /var/task

# Copy requirements and install dependencies
COPY requirements.txt .

# Install system dependencies for lxml and other C extensions
RUN yum install -y libxml2-devel libxslt-devel gcc && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    yum clean all

# Copy the rest of the application code
COPY . .

# Set the Lambda handler (main.py with Mangum)
CMD ["main.handler"] 