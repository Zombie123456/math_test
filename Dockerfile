FROM python:3.7.0
ENV PYTHONUNBUFFERED 1
RUN mkdir /mathtest
WORKDIR /mathtest
EXPOSE 8000
COPY . /mathtest/
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["/mathtest/entrypoint.sh"]
