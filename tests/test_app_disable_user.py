import json

from users.disableUser import app


def test_lambda_handler():
    evento = {
        'headers': json.dumps({
            'Authorization': 'eyJraWQiOiJ5dzNxRVwvUFlaY3lJZTh0QUUrWUg1S3hZWjR2U1pJMlhVNVVmVGhHZU9DWT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJmNGE4ZTRjOC0wMGYxLTcwMDUtYmQ0MS1hYzI0OGUwM2EyMDAiLCJjb2duaXRvOmdyb3VwcyI6WyJhZG1pbmlzdHJhZG9yZXMiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xXzFIQWpIMWZLaiIsImNvZ25pdG86dXNlcm5hbWUiOiJhZG1pbiIsIm9yaWdpbl9qdGkiOiJlM2IxMzk1Yy1mM2E5LTQxYTEtYmMzMS0xMmI4YjAyYjU4NGEiLCJhdWQiOiI3cWVwb28yOHNhbTlhaGJmdTNiZW1kajg0MyIsImV2ZW50X2lkIjoiODY3NTlmNzYtZTgwMi00MWRkLWExOGUtZTQ3NGQ5YjIyZTkzIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MTk2MDkyMzksImV4cCI6MTcxOTYxMjgzOSwiaWF0IjoxNzE5NjA5MjM5LCJqdGkiOiI5NGUzOTUzOS1kMjJiLTQ4NDAtYTE3Mi1lNjNhMTNiM2Q4OGUiLCJlbWFpbCI6IjIwMjEzdG4xMjhAdXRlei5lZHUubXgifQ.FdJq1zIHgcfJCnICTkvILLMgmhhDnEwDVuXc9M927L7TirCHdTxsw9qK1N3aWNM4Knay95yJnNuZHKr3jLmtyXFSPBqeF0KKBneCux3qDRwH90TjoSkThAli-F8E9of3VauPurM3XHWmvBHrgHgPKtyQ-ghzG4nRxd_AehYkf4PyLw__m1ajnhgxAOtntju0h_mGOszyn-_O9h5LJVIlcaaksKLsIHc5kyJTqXYPW6Hc7NhQExhfHeWFVEQAKPM15XzPWW0j8gSCBZZZTL5kAYWgDbd4ohlcCQ7WYqsV5G57Wlgi3lhpcK66lV1ukH6ZvubkRS9M1IfyCz0jsM2W7A'
        }),
        'body': json.dumps({
            'id': 3
        })
    }
    response = app.lambda_handler(evento, "")
    print(response)
