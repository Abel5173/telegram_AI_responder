import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai import generate_response

# Use dummy user/chat IDs for testing
user_id = 1
chat_id = 1

print("Type 'exit' to quit.")
while True:
    user_message = input("You: ")
    if user_message.lower() == "exit":
        break
    response = generate_response(user_id, chat_id, user_message)
    print("AI:", response) 