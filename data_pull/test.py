import google.generativeai as genai

# Set your Gemini API key
genai.configure(api_key="AIzaSyA_a9dk5E0LvqTsDl8n5qmGjOckX4p8T4M")

# Initialize a model (Gemini-pro is for text-only tasks)
model = genai.GenerativeModel("gemini-2.0-flash")

# Generate content
AQI = 200
respiratory_ailment = "Bronchitis"
location = "Rabindra Bharati University, Kolkata - WBPCB"
content = f"I stay in {location}, I have {respiratory_ailment} and the current AQI here is {AQI}, can you generate some precautions to take and any emergency hospitals if required?"

response = model.generate_content(content)

# Print the generated text
print(response.text)
# # from google import genai


# client = genai.Client(api_key="AIzaSyA_a9dk5E0LvqTsDl8n5qmGjOckX4p8T4M")

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=content,
# )

# print(response.text)

