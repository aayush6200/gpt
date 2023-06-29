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
    l3_data = json.load(file)


# system_message = f''' "role":'system', "content":'As an assistant, your role is to provide information to user from {l3_data} by listening user queries'''


def save_response(email, text, res):
    try:
        chat_message = ChatMessage(
            email=email,
            user_message=text,
            chatgpt_response=res
        )

        chat_message.save()
        print('saved')
        return
    except ValueError as e:
        raise e

    print('saved')


# generating response from gpt


def get_gpt_response(email, message, text, model='gpt-3.5-turbo'):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=message,
            temperature=0
        )

        # saving response calling the function in database
        try:
            save_response(
                email, text, response.choices[0].message['content'])

            return response.choices[0].message['content']
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
                message = [
                    {'role': 'system', 'content': f'You are an assistant who responds in \
                     2 sentences max using {l3_data}'},
                    {'role': 'user', 'content': f'{text}'}
                ]
                # prompt = "please provide at max 2 sentence help to user"

                try:
                    response = get_gpt_response(
                        email, message, text)

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


def get_response(request):
    if request.method == 'GET':
        email = request.email
        print('get messages', email)

        if email:
            try:
                chat_messages = ChatMessage.objects.filter(email=email)
                # creating a list of dictionaries for each message and responses

                chats = [{'user_chat': msg.user_message,
                          'gpt_chat': msg.chatgpt_response, 'id': msg.id} for msg in chat_messages]
                return JsonResponse(chats, status=200, safe=False)
            except Exception as e:
                print('error', e)
                return JsonResponse({'message': 'internal server error'}, status=500)
        else:
            return JsonResponse({'message': 'error occurred'}, status=500)


@csrf_exempt
def verify_token(request):

    response_data = {
        'message': 'token verified',
        'token': request.token
    }

    return JsonResponse(response_data, status=200)
