import grequests
from config import yandex_iam_token, folder_token

IAM_TOKEN = yandex_iam_token
folder_id = folder_token


def translate(texts: str | list, target_language='ru') -> str:
    body = {
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(IAM_TOKEN)
    }

    response, = grequests.map([grequests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                              json=body,
                                              headers=headers
                                              )])

    return response.json()['translations'][0]['text']


if __name__ == '__main__':
    print(translate('Погода в Москва Clear', 'en'))
    print(translate('Weather in Moscow Clear', 'ru'))
