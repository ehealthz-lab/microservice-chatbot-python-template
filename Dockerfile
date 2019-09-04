# Use an official Python runtime as a parent image
FROM python:3.7.0

#Set some environment vars
ENV LANG C.UTF-8
ENV TZ Europe/Madrid
ENV DEBIAN_FRONTEND noninteractive

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Make port 25052 available to the world outside this container
EXPOSE 25052

# Run app.py when the container launches
CMD ["python", "app.py"]