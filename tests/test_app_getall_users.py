import json
from users.getAllUsers import app

def test_lambda_handler():
    evento = {
        'headers': json.dumps({
            'Authorization': 'eyJraWQiOiJrck9pSWUxSkdXZGx5bitnRFBrNUlEMlwvRWVPQW5iWjhVYkQ2REg4Z3FnVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJkNGE4YzRiOC0xMDAxLTcwY2YtNzhkNy1jNmNiNjYxZGVkNjkiLCJjb2duaXRvOmdyb3VwcyI6WyJBZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfN3dMdDg1TWF2IiwiY29nbml0bzp1c2VybmFtZSI6ImFkbWluIiwib3JpZ2luX2p0aSI6IjNlZDU4OWFlLTgwZjItNDIyMS1iMjI3LTk1YTgxNDkwZDcyOSIsImF1ZCI6IjdvdHM4cjVldDZmYjBrMnQ3aHBiNWVhOTg0IiwiZXZlbnRfaWQiOiJjZWU2NTM2Yy0wOTMyLTRmMmMtOTNlOS1mOGVmOWFlYTE4NzMiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcyMjk2NTc2NSwiZXhwIjoxNzIyOTY5MzY1LCJpYXQiOjE3MjI5NjU3NjUsImp0aSI6ImZiMDg5NjA0LWE3ZGYtNDQyYS1iMDMyLWQ1ODNhODE3MjljYSIsImVtYWlsIjoiZW1pLm9ydGl6Lmhlcm5hbmRlekBnbWFpbC5jb20ifQ.BMiYFxbYwrsth8RIko1w0qeW_tfXSSFktPLYxDUAZoZ1Bu53Nk7dfv7ClATMVD0GEahFGLyp-ilscRLsyRn0J5pssjDVV0Y7eUn0NOHHxFxKldryGwk1KPoe_JUywYsx-9garAPg-lSCZANeOVhv7Cp7MqB_e2QAsvNmzy3jx55fe3m2Q784q_rPOXi69Lfrxo0cIfRyJJ5zGYWuAJjkXFhfTjJIZNsdLphwsjuQGo0f50FLo0ztjIweb6fJmuXUPn-ZgyrUP-gMXb96P2llokxdBVT5dbVfTKfYp5BFwagszUb12YMtD2zyapk8hMoMU1FsC51-D2CFoG6_SrRCyg'
        }),
    }

    response = app.lamda_handler(evento, "")
    print(response)