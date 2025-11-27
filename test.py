import google.generativeai as genai

genai.configure(api_key="AIzaSyD4a6WDAY_Q9G0ljwIesix1Vd8OzYTKz94")

for model in genai.list_models():
    print(model.name, model.supported_generation_methods)
