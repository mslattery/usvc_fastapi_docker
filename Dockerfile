# Dockerfile

# 1. Use an official AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.12

# 2. Copy the requirements file into the image
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# 3. Install the specified packages
RUN pip install -r requirements.txt

# 4. Copy the application code
COPY main.py ${LAMBDA_TASK_ROOT}

# 5. Set the command to run when the container starts.
# The format is {filename}.{handler_variable_name}
CMD [ "main.handler" ]
