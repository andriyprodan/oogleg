FROM continuumio/miniconda3

WORKDIR /app
COPY environment.yml .
RUN conda env create -f environment.yml
#COPY requirements.txt .
#RUN conda create --name oogleg --file requirements.txt --yes

SHELL ["conda", "run", "-n", "oogleg", "/bin/bash", "-c"]

# RUN pip install hunspell

# Activate the environment, and make sure it's activated:
RUN conda activate myenv
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"


COPY . ./
EXPOSE 8000