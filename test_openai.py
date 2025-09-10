from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key="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")

try:
    # Use chat completions
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=50,
        temperature=0.7
    )

    # Print the response content
    print("Response:")
    print(response.choices[0].message.content)

except Exception as e:
    # Log any exceptions
    print(f"Error: {e}")
