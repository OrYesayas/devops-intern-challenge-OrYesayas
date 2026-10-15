FROM python:3.11-alpine

# Don't buffer stdout -- otherwise test output only appears when the
# process exits, which is useless while you are debugging a hang.
ENV PYTHONUNBUFFERED=1

WORKDIR /tests
COPY test_integration.py .

CMD ["python", "test_integration.py"]
