FROM python:3
ENV PYTHONUNBUFFERED 1
WORKDIR /app/backend
# Install & use pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy && pipenv install
COPY . ./
EXPOSE 8000