FROM python

COPY . app/ng-backend
WORKDIR /app/ng-backend

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "api.main:app"]