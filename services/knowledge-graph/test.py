import json

import openai

from src.settings import settings

YANDEX_CLOUD_FOLDER = settings.yandexcloud.folder_id
YANDEX_CLOUD_API_KEY = settings.yandexcloud.apikey

client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1",
    project=YANDEX_CLOUD_FOLDER,
)

models = client.models.list()

print(models.data)

# Функция Погода
def get_current_weather(location):
    return {"location": location, "temperature": -22, "weather_condition": "Солнечно"}

# Функция Калькулятор
def calculator(a, b):
    return a + b

def run_conversation(user_input):
    selected_model = f"gpt://{YANDEX_CLOUD_FOLDER}/yandexgpt/rc"

    # Задание функций
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Получение текущей погоды для указанного местоположения",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Местоположение"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Сложить два числа",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "int",
                            "description": "Первое число"
                        },
                        "b": {
                            "type": "int",
                            "description": "Второе число"
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        }
    ]

    # Выполнение запроса
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "user", "content": user_input}
        ],
        tool_choice="auto",
        tools=tools
    )

    # Ответ модели
    message = response.choices[0].message
    print(message)

    # Вызов запрошенных моделью функций
    if message.tool_calls:
        # Массив сообщений для отправки результатов выполнения
        new_messages = [
            {"role": "user", "content": user_input},
            message
        ]

        # Заполнение результата для каждой вызванной функции
        for tool_call in message.tool_calls:

            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_weather":
                function_response = get_current_weather(function_args.get("get_current_weather"))
                new_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_response)
                })

            if function_name == "calculator":
                function_response = calculator(function_args.get("a"), function_args.get("b"))
                new_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_response)
                })

        second_response = client.chat.completions.create(
            model=selected_model,
            messages=new_messages,
            tools=tools
        )

        # Ответ модели с учетом вызова функций
        return second_response.choices[0].message.content

    # Функции не был вызваны, возвращаем исходный ответ
    return message.content


if __name__ == "__main__":
    result = run_conversation("2+2 и погода в москве")
    print(result)
