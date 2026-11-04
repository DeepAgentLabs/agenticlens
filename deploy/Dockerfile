FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir '.[api]' && useradd --uid 10001 --create-home lens \
    && mkdir /data && chown lens /data
USER 10001:10001
ENV LENS_DATABASE=/data/lens.db
EXPOSE 8000
CMD ["uvicorn", "agenticlens.enterprise.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
