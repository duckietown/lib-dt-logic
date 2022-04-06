FROM python:3.7

# working directory and environment config
WORKDIR /library
ENV DISABLE_CONTRACTS=1

# install requirements via pip
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# copy everything
COPY . .

# show list of files copied
RUN find .

# install modules
RUN pipdeptree
RUN python setup.py develop --no-deps
