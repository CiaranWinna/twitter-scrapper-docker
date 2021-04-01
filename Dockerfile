FROM python:3.6

EXPOSE 5000

WORKDIR /app

COPY ./app /app

RUN pip install -r requirements.txt

RUN set FLAST_PATH=app.py

# Depending on the setup of the local system, the command may need 
# to be changed to 'flask run' 
CMD python app.py