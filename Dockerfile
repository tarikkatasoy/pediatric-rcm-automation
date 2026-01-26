FROM public.ecr.aws/lambda/python:3.13

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies including pyarrow
RUN pip install -r requirements.txt

# Copy all code and agents
COPY . ${LAMBDA_TASK_ROOT}

# Set the handler
CMD [ "handler.lambda_handler" ]
