from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained("allenai/OLMo-2-0425-1B")
tokenizer = AutoTokenizer.from_pretrained("allenai/OLMo-2-0425-1B")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

inputs = tokenizer("Hello", return_tensors="pt").to(device)
outputs = model.generate(**inputs, max_length=20)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
