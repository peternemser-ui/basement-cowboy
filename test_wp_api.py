import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarize the following: 'Artificial Intelligence is transforming the world.'"}
    ],
    max_tokens=100
)

print(response['choices'][0]['message']['content'])
