FROM python

COPY . app/ng-backend
WORKDIR /app/ng-backend

RUN pip install -r requirements.txt

ENV DB_ADMIN_USER=mainAdmin
ENV DB_ADMIN_PASSWD=XF8J:SizM%4kcr11

ENTRYPOINT ["uvicorn", "api.main:app"]