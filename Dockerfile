FROM python:3

ADD build_tag_push.py /

RUN pip install -r requirements.txt

CMD python ./build_tag_push.py