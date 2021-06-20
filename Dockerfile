FROM bildcode/pyside2

COPY . .

RUN chmod +x start.sh && pip3 install -U pip && pip install -Ur requirements.txt

CMD ["./start.sh"]