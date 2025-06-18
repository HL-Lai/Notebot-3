import os
import re
import base64
import openai
import mimetypes
from dotenv import load_dotenv

load_dotenv()

def clean_string(input_string):
    # Use regex to keep only alphanumeric characters
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', input_string)
    return cleaned_string

def history_default():
    return [{"role": "system", "content": "You are a helpful assistant who helps to write notes. You may also answer user's questions if they have query. You write or correct notes according to the user's input. Keep your response concise. Answer directly without any polite phrases or conclusions. You may have a title, but don't write any openings before the title, but after the title. If there is title, use <h1> (the largest heading) for the title. Use latex for any math symbols. Use 4 spaces for any indentations. Better use <ol> and <ul> tags for lists. Use HTML tags for tables."}]

def select_model(model_input):
    match model_input:
        case 'GPT-4.1-nano': return 'gpt-4.1-nano'
        case 'GPT-4.1-mini': return 'gpt-4.1-mini'
        case 'GPT-4.1': return 'gpt-4.1'
        case 'o4-mini': return 'o4-mini'
        case 'GPT-4o': return 'gpt-4o'
        case 'GPT-4': return 'gpt-4'
        case 'GPT-3.5': return 'gpt-35-turbo'
        case _: return model_input

def is_image_file(filepath):
    if not os.path.isfile(filepath):
        return False
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('image/'):
        return True
    return False

def process_image(image_input):
    """
    image_input may be:
      • a filesystem path to an image
      • a data URI (e.g. "data:image/png;base64,....")
      • a raw base64 string (no data: prefix)
    """
    # 1) If it’s an existing file on disk and looks like an image:
    if isinstance(image_input, str) and os.path.isfile(image_input) and is_image_file(image_input):
        mime, _ = mimetypes.guess_type(image_input)
        with open(image_input, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:{mime};base64,{b64}"

    # 2) If it’s already a full data‐URI, just return it
    if isinstance(image_input, str) and image_input.startswith("data:"):
        return image_input

    # 3) If it’s raw base64 (no “data:”), slap on a default mime
    _BASE64_ONLY = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')
    if isinstance(image_input, str) and _BASE64_ONLY.fullmatch(image_input):
        # you may want to pass in the desired mime type
        # default_mime = "image/png"
        return f"data:image/;base64,{image_input}"

    raise ValueError("The provided input is not a valid image file or base64 string.")

def chatbot(message=False, image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key=None, api_endpoint=None, api_version=None, defining=False):
    model=select_model(model)
    temperature = 1 if model in ['o4-mini', 'DeepSeek-R1'] else temperature
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            api_key = clean_string(input("Please input your api key: ").strip())
    
    if api_endpoint is None:
        api_endpoint = os.getenv('OPENAI_API_ENDPOINT', "https://api.hku.hk")

    if api_version is None:
        api_version = os.getenv('OPENAI_API_VERSION', "2025-01-01-preview")

    client = openai.AzureOpenAI(
        azure_endpoint=api_endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    history[0]['content'] = prompt
    if (model.startswith('gpt') or model == 'o4-mini') and image:
        # with open(image, "rb") as image_file:
        #     image = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode()
        image = process_image(image)
        content = []
        if message:
            content.append({"type": "text", "text": message})
        content.append({"type": "image_url", "image_url": {"url": image}})
        new_prompt = {"role": "user", "content": content}
    else:
        new_prompt = {"role": "user", "content": message}
    history.append(new_prompt)
    # completion = openai.ChatCompletion.create(engine="chatgpt", messages=history)
    response = client.chat.completions.create(model=model, messages=history, temperature=temperature)
    answer = response.choices[0].message.content
    if defining: history.pop()
    elif not defining:
        history.append({"role": "assistant", "content": answer})
    return history, answer

##################################################################################################

def main(message=False, image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key='', defining=False):
    history, answer = chatbot(message=message, image=image, model=model, prompt=prompt, temperature=temperature, history=history, api_key=api_key, defining=defining)
    print(answer)

if __name__ == "__main__":
    # main(message="Hi!", image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key=None, defining=False)
    main(message="What is this?", image="test.jpg", model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key=None, defining=False)