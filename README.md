## Что реализовано

- Настроена база знаний в Supabase с `pgvector`.
- PDF `Оптимизация IT менеджмента.pdf` разбит на чанки и проиндексирован через embeddings.
- В n8n собран RAG workflow:
  - `Webhook`
  - `AI Agent`
  - `Groq Chat Model` (Вместо 'llama-3.3-70b-versatile', которая была отключена 16 августа 2026 года, используется 'gpt-oss-120b')
  - `Supabase Vector Store`
  - Hugging Face embeddings
- Frontend планера подключён к n8n через `fetch`.
- Ответы RAG-агента отображаются прямо в интерфейсе AI-чата.
- Добавлен простой Python proxy-сервер для same-origin запросов.
- Web App опубликован через Cloudflare Tunnel.
- Приложение подключено к Telegram Bot как Telegram Web App.
