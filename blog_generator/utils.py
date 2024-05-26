import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import random

load_dotenv()

api_key = os.environ.get('HUGGINGFACE_API_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {api_key}"}

def format_prompt(message, custom_instructions=None):
	prompt = ""
	if custom_instructions:
		prompt += f"[INST] {custom_instructions} [/INST]"

	prompt += f"[INST] {message} [/INST]"
	return prompt

def generate(prompt, temperature=0.7, max_new_tokens=1000, top_p=0.95):
	temperature = float(temperature)

	if temperature < 1e-2:
		temperature = 1e-2

	top_p = float(top_p)

	generate_kwargs = dict(
		temperature=temperature,
		max_new_tokens=max_new_tokens,
		top_p=top_p,
		seed = random.randint(0, 10**7),
	)


	custom_instructions = "There shoule no titles. Don't include a Title, remove if there is one there. Make your reponses short and to the point. You are a professional article writer.  Based on the following transcript from a YouTube video, write a article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper article:\n\n{transcript}\n\n"
	formatted_prompt = format_prompt(prompt, custom_instructions)

	client = InferenceClient(API_URL, headers=headers)

	response = client.text_generation(formatted_prompt, **generate_kwargs)

	generated_content = response

	return generated_content

