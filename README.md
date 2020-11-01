# LPSCopModel
Web interface for empirical copula modeling as a tool developed for using along a PhD degree in University of São Paulo, working with the LPS - Laboratório de Processamento de Sinais (Signal Processing Lab) team at EESC São Carlos - São Paulo - Brazil.


*** Installation ***

This software is based on a python django platform running locally or in a web server, so maybe you can access it by a web browser if someone has previously deployed it on a web server or installing it locally by yourself in a local django environment.

If the former is your case, first you will need a python environment in your computer. This software was developed upon a python 3.7.3 environment with the following requirements:

django==2.2.5

gunicorn==20.0.0

django-heroku==0.3.1

pandas==0.24.2

geopandas==0.6.1

matplotlib==3.1.0

numpy==1.17.1

scipy==1.3.1

dbfread==2.0.7

pymc3==3.5

python-dotenv==0.14.0

dj-database-url==0.5.0

descartes==1.1.0

theano==1.0.4

Then, we recommend for you to follow instructions for installing a python environment with django in you computer, for example by reading django documentation at https://docs.djangoproject.com/en/3.1/.

After that you can download this complete repository to any folder in you computer, as long as you keep its name unchanged.

For starting the local host web service and allowing your web browser to access the sofware, you have to open a terminal, go to the downloaded project directory and run the start django server command "python manage.py runserver".

That's it! For using the software the only thing you must do is to open your web browser and navigate to "127.0.0.1:8000" or "localhost:8000" and the software home page will appear.

Good work from there!!!
