from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import requests
import openai
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Student
import pandas as pd

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FLASK_API_URL = 'http://127.0.0.1:5000/api/students'
CHATGPT_API_URL = "http://127.0.0.1:5000/api/chatgpt" 



def product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/product_list.html', {'products': products})




def get_flask_students(request):
    try:
        response = requests.get(FLASK_API_URL)
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': 'Failed to fetch data from Flask API'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_flask_student_by_id(request, student_id):
    try:
        response = requests.get(f'{FLASK_API_URL}/{student_id}')
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({'error': f'Failed to fetch student with ID {student_id} from Flask API'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        grade = request.POST.get('grade')

        if name and grade:
            data = {'name': name, 'grade': grade}
            response = requests.post(FLASK_API_URL, json=data)
            if response.status_code == 201:
                return render(request, 'myapp/success.html', {'message': 'Student added successfully!'})
            else:
                return render(request, 'myapp/error.html', {'message': 'Failed to add student. Please try again.'})
        else:
            return render(request, 'myapp/error.html', {'message': 'Missing required fields: name or grade.'})

    return render(request, 'myapp/add_student.html')




def update_student(request, student_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        grade = request.POST.get('grade')

        if name and grade:
            data = {'name': name, 'grade': grade}
            response = requests.put(f'{FLASK_API_URL}/{student_id}', json=data)
            if response.status_code == 200:
                return render(request, 'myapp/success_put.html', {'message': 'Student updated successfully!'})
            else:
                return render(request, 'myapp/error_put.html', {'message': 'Failed to update student. Please try again.'})
        else:
            return render(request, 'myapp/error_put.html', {'message': 'Missing required fields: name or grade.'})

    response = requests.get(f'{FLASK_API_URL}/{student_id}')
    if response.status_code == 200:
        student = response.json()
        return render(request, 'myapp/update_student.html', {'student': student})
    else:
        return render(request, 'myapp/error_put.html', {'message': 'Student not found.'})




def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})




def delete_student(request, student_id):
    if request.method == "GET":
        return render(request, "myapp/confirm_delete.html", {"student_id": student_id})

    elif request.method == "DELETE":
        try:
            response = requests.delete(f"{FLASK_API_URL}/{student_id}")
            if response.status_code == 200:
                return render(request, "myapp/success.html", {"message": f"Student with ID {student_id} deleted successfully!"})
            elif response.status_code == 404:
                return render(request, "myapp/error.html", {"error": f"Student with ID {student_id} not found."})
            else:
                return render(request, "myapp/error.html", {"error": f"Failed to delete student: {response.json()}"})
        except requests.exceptions.RequestException as e:
            return render(request, "myapp/error.html", {"error": f"Error communicating with Flask API: {e}"})
    else:
        return JsonResponse({'myapp/error': 'Invalid request method.'}, status=405)




def chatgpt_text_generation(request):
    if request.method == "GET":
        try:
            prompt = "Generate a simple greeting message."

            # Make the API call to OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the generated message
            generated_message = response['choices'][0]['message']['content']

            # Return the generated message in a JSON response
            return JsonResponse({"message": generated_message}, status=200)

        except openai.error.RateLimitError:
            # Handle rate limit exceeded error
            return JsonResponse({"error": "You have exceeded the API usage quota. Please try again later."}, status=429)
        
        except openai.error.APIError as e:
            # Handle general API errors
            return JsonResponse({"error": f"An error occurred with the API: {str(e)}"}, status=500)
        
        except openai.error.AuthenticationError:
            # Handle authentication errors (invalid API key)
            return JsonResponse({"error": "Authentication error. Please check your API key."}, status=401)
        
        except openai.error.Timeout:
            # Handle timeout errors
            return JsonResponse({"error": "The request to OpenAI timed out. Please try again later."}, status=504)
        
        except Exception as e:
            # Handle any other unexpected errors
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    # If the request method is not GET
    return JsonResponse({"error": "Invalid request method. Please use GET."}, status=405)


# Define a DataFrame to store chat history (initially empty)
chat_history_df = pd.DataFrame(columns=["query", "response"])

def save_to_csv(df):
    """Function to save the chat history to a CSV file."""
    df.to_csv("chat_history.csv", index=False)

# This view renders the ChatGPT chatbox template
def chatgpt_chat(request):
    """Render the ChatGPT chatbox template."""
    return render(request, "myapp/chatgpt_chat.html")

@csrf_exempt  # Disable CSRF protection for this view
def chatgpt_api(request):
    """Handle requests from the frontend and send them to the Flask API."""
    global chat_history_df  # Use the global DataFrame to store chat history

    if request.method == "POST":
        try:
            # Parse the JSON body of the request
            data = json.loads(request.body.decode('utf-8'))
            user_query = data.get("query", "").strip()

            # Validate the query: if empty, return a 400 error
            if not user_query:
                return JsonResponse({"error": "Query cannot be empty"}, status=400)

            # Define the headers for the request to the Flask API
            headers = {"Content-Type": "application/json"}
            payload = {"prompt": user_query}

            try:
                # Send the request to the Flask API
                response = requests.post(CHATGPT_API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    # Get the response from the Flask API
                    chatgpt_response = response.json().get("message", "No response from Flask API")

                    # Log the query and response into the pandas DataFrame
                    new_entry = pd.DataFrame({"query": [user_query], "response": [chatgpt_response]})
                    chat_history_df = pd.concat([chat_history_df, new_entry], ignore_index=True)

                    # Save the updated DataFrame to a CSV file
                    save_to_csv(chat_history_df)

                    # Return the response to the frontend
                    return JsonResponse({"message": chatgpt_response}, status=200)

                else:
                    return JsonResponse(
                        {"error": f"Flask API returned an error: {response.status_code}", "details": response.text},
                        status=response.status_code,
                    )
            except requests.exceptions.RequestException as e:
                return JsonResponse({"error": f"Error connecting to Flask API: {str(e)}"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
 
