# Hugging Face Spaces (Docker) yoki istalgan server uchun
FROM python:3.12-slim

# HF Spaces konteynerni 1000-foydalanuvchi sifatida ishga tushiradi
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH PYTHONUNBUFFERED=1 \
    TORCH_THREADS=2 HF_HOME=/home/user/.cache/huggingface
WORKDIR /home/user/app

COPY --chown=user requirements.txt requirements-full.txt ./
RUN pip install --no-cache-dir --user -r requirements-full.txt
COPY --chown=user . .

EXPOSE 7860
# Space sozlamalarida: TRIAGE_MODELS_REPO (variable), OPERATOR_PASSWORD va TRIAGE_SECRET (secrets)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
