import openai
from flask import current_app

def rewrite_text(original_text):
    openai.api_key = current_app.config['OPENAI_API_KEY']
    assistant_id = current_app.config['OPENAI_ASSISTANT_ID']

    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=original_text
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            break
        elif run.status in ["failed", "cancelled", "expired"]:
            raise Exception(f"Run failed: {run.status}")

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    reply = next((m for m in reversed(messages.data) if m.role == "assistant"), None)
    return reply.content[0].text.value if reply else "[Ошибка генерации]"
