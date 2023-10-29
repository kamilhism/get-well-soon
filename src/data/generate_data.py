import os
import openai
import json

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
if api_key != "":
    openai.api_key = api_key
else:
    print("Warning: OPENAI_API_KEY is not set")

data_type = sys.argv[1]

if data_type == "sick":
    prompt_part = "not felling good and ill"
    output_file_name = "sick"
elif data_type == "not_sick":
    prompt_part = "felling good and not ill"
    output_file_name = "not_sick"
else:
    print("Invalid data_type argument. Use 'sick' or 'not_sick'.")
    sys.exit(1)

count = sys.argv[2]

prompt = f"Generate {count} messages in English where person claims that is {prompt_part}. Respond in json with array of messages: {{'messages': []}}"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
          "role": "user",
          "content": prompt
        }
    ],
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7,
)
generated_messages = response["choices"][0]["message"]["content"]["messages"]

with open(f"../../data/raw/{output_file_name}.txt", "w") as file:
    for message in generated_messages:
        text = re.sub(r"[^\w\s.]", " ", message)
        file.write(text.strip() + "\n")
