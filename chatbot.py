import os
import re
import openai
from dotenv import load_dotenv

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
    import mimetypes
    mime, _ = mimetypes.guess_type(filepath)
    if mime and mime.startswith('image/'):
        return True
    return False

def process_image(image_path):
    if isinstance(image_path, str): # assume base64 already
        image_data = f"data:image/;base64,{image_path}"
        return image_data
    elif image_path and is_image_file(image_path):
        with open(image_path, "rb") as image_file:
            mime, _ = mimetypes.guess_type(image_path)
            base64_str = base64.b64encode(image_file.read()).decode()
            image_data = f"data:{mime};base64,{base64_str}"
        return image_data
    else:
        raise ValueError("The provided file is not a valid image.")

def chatbot(message=False, image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key='', defining=False):
    # print(image[:20])
    model=select_model(model)
    temperature = 1 if model in ['o4-mini', 'DeepSeek-R1'] else temperature
    if api_key is None:
        key = input("Please input your api key: ").strip()
        api_key = clean_string(key)

    load_dotenv()

    client = openai.AzureOpenAI(
        azure_endpoint=os.getenv('OPENAI_API_ENDPOINT'),
        api_key=api_key,
        api_version="2025-01-01-preview"
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
    chatbot(message=message, image=image, model=model, prompt=prompt, temperature=temperature, history=history, api_key=api_key, defining=defining)

if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY', None)
    if api_key is None:
        key = input("Please input your api key: ").strip()
        api_key = clean_string(key)

    main(message="Hi!", image=False, model="gpt-4.1", prompt="You are a helpful assistant who helps to write notes.", temperature=0.7, history=history_default(), api_key='', defining=False)
