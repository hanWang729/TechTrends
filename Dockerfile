# Use a Python based image in verwsion 2.7
From python:2.7

COPY . .
WORKDIR /techtrends

# Expose the application port 3111
EXPOSE 3111
# Install packages defined in the requirements.txt file
RUN pip install -r ./requirements.txt
# Ensure that the database is initialized with the pre-defined posts in the init_db.py file
RUN python init_db.py
# The application should execute at the constainer start
CMD ["python","app.py"]
