FROM python:3.9.4

# create the app user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0


# Install Poetry
# RUN curl -sSL https://github.com/python-poetry/install.python-poetry.org/ | POETRY_HOME=/opt/poetry  python3 - && \
#     cd /usr/local/bin && \
#     ln -s /opt/poetry/bin/poetry && \
#     poetry config virtualenvs.create false

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* ./app/run.sh /app/

ENV PATH="/app/.venv/bin:$PATH"

RUN poetry --version

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=true

# Install dependencies
RUN if [ $INSTALL_DEV ]; then \
      poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
      poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi

RUN echo $PATH

# chown all the files to the app user
COPY --chown=app:app ./app /app
RUN chmod +x run.sh


ENV PYTHONPATH=/app

# change to the app user
# Switch to the non-root user.
USER app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
CMD ["./run.sh"]
