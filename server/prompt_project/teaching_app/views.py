from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ChatMessage

# Create your views here.
_ = load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']
gtp_model = os.environ['gpt_model']


# importing and opening json files

json_file_path_l3 = "JSON/l3.json"
json_file_path_l4 = "JSON/l4.json"

with open(json_file_path_l3) as file:
    positions = json.load(file)


prompt = f"""
- If the user wants to provide their qualifications, analyze their qualifications and recommend the best position from the {positions}. If the user is uncertain about what they are looking for, respond kindly and ask for clarification.

Please follow the above steps to assist users with their queries.
"""


# saves the user information
def save_response(email, text, res):
    try:

        # saving user and gpt response for analyzing results for future queries

        if (len(text) > 0 and len(res) == 0):
            chat_message = ChatMessage(
                email=email,
                user_message=text,

            )
            chat_message.save()
        elif (len(res) == 0):
            chat_message = ChatMessage(
                email=email,
                chatgpt_response=res
            )

            chat_message.save()
        print('saved')
        return
    except ValueError as e:
        raise e

    print('not saved')

# getting response from gpt model using db.This will be used for analysis purpose


def gpt_analysis(user_email, text, model='gpt-3.5-turbo'):

    # Retrieve the latest conversations involving the specific user
    latest_conversations = ChatMessage.objects.filter(
        email=user_email).order_by('-created_at')[:10]

    # Concatenate user's messages to form conversation history
    conversation_history = ''

    for conv in latest_conversations:
        conversation_history += "User: " + conv.user_message + "\n"
        conversation_history += "GPT: " + conv.chatgpt_response + "\n"

        # Prepare instructions or prompts for GPT
        instructions = f"You are analyzing the conversation with the user.\
            Generate insights based on the following conversation history and respond politely\
                :Use {prompt} for further insights\
                Only provide answer don't provide answer like:based on user response  \n\n"
        input_prompt = instructions + '\n' + conversation_history

    # Generate reply from GPT
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'system', 'content': input_prompt},
                      {'role': 'user', 'content': text}],
            temperature=0
        )

        # only saving results from gpt
        save_response(
            user_email, '', response.choices[0].message['content'])
        return response.choices[0].message['content']
    except Exception as e:
        print('internal error', e)

# gets list of all the data for analysis


# def get_data_for_analysis(email):
#     print('get messages', email)

#     if email:
#         try:
#             chat_messages = ChatMessage.objects.filter(email=email)
#             # creating a list of dictionaries for each message and responses

#             chats = [{'user_chat': msg.user_message,
#                       'gpt_chat': msg.chatgpt_response, 'id': msg.id} for msg in chat_messages]

#             # returning successful messages and chats for analysis
#             response_message = 'data for query received'
#             print('at data analysis', chats)
#             return ([chats, response_message])

#         except Exception as e:
#             print('error', e)

#     # returning error messages
#     response_message = 'error for query/may be internal error'
#     return [response_message]


# generating response from gpt
def get_gpt_response(email, text, model='gpt-3.5-turbo'):
    try:
        print('hello wo')
        # response = openai.ChatCompletion.create(
        #     model=model,
        #     messages=message,
        #     temperature=0.8
        # )

        # saving response calling the function in database
        try:

            # saving query from user for future use
            save_response(
                email, text, '')

            # # calling analysis function for getting data to analyze using gpt
            # data_to_analyze = get_data_for_analysis(email)
            # if len(data_to_analyze) > 1:
            # calling gpt to analyze data from the previous conversations
            after_gpt_response = gpt_analysis(email, text)
            return after_gpt_response

        except ValueError as e:
            raise e
    except openai.OpenAIError as e:
        # Handle OpenAI API errors
        print("OpenAI API error:", str(e))
    except Exception as e:
        # Handle other exceptions
        print("An error occurred:", str(e))


# getting data from client
@ensure_csrf_cookie
@csrf_exempt
def generate_response(request):
    email = request.email  # getting email from the middleware token
    body = request.body.decode('utf-8')  # decoding the body from the request

    try:
        if email and body:
            text = json.loads(body)  # parsing the body from the request
            text = text.get('userChat')
            print('text:', text)
            if text:

                try:
                    # calling gpt model from another function
                    response = get_gpt_response(
                        email,  text)

                    response_data = {
                        'message': 'gpt replied successfully',
                        'user_query': text,
                        'gpt_response': response,
                        'token': request.token

                    }

                    return JsonResponse(response_data, status=200)
                except ValueError as e:
                    return JsonResponse({'message': "internal server error"}, status=200)
            else:
                response_data = {
                    'message': 'no response from gpt',
                    'chat': 'internal server error'
                }
                return JsonResponse(response_data, status=500)
    except Exception as e:
        # Handle the exception
        print("An error occurred:", str(e))
        response_data = {
            'message': 'an error occurred',
            'chat': 'internal server error'
        }
        return JsonResponse(response_data, status=500)


# getting response from gpt model using db.
# def get_response(request):
#     if request.method == 'GET':
#         email = request.email
#         print('get messages', email)

#         if email:
#             try:
#                 chat_messages = ChatMessage.objects.filter(email=email)
#                 # creating a list of dictionaries for each message and responses

#                 chats = [{'user_chat': msg.user_message,
#                           'gpt_chat': msg.chatgpt_response, 'id': msg.id} for msg in chat_messages]
#                 return JsonResponse(chats, status=200, safe=False)
#             except Exception as e:
#                 print('error', e)
#                 return JsonResponse({'message': 'internal server error'}, status=500)
#         else:
#             return JsonResponse({'message': 'error occurred'}, status=500)


@csrf_exempt
def verify_token(request):

    response_data = {
        'message': 'token verified',
        'token': request.token
    }

    return JsonResponse(response_data, status=200)
