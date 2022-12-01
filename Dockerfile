FROM python:3.10.4
ENV TZ="Asia/Bangkok"
COPY . /opt/app
WORKDIR /opt/app
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -U discord.py
RUN pip install -U Jinja2
CMD ["python", "curve_3pool.py"]