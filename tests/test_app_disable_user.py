import json

from users.disableUser import app


def test_lambda_handler():
    evento = {
        'headers': json.dumps({
            'Authorization': 'eyJraWQiOiJEOFZsWlcxVTRnRWFQWEQyT2VROUJJNVdEczlTVGJsT0QwZmRpTnlMckZVPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJiNDY4YzQ5OC02MGQxLTcwNzUtMDJlOS0xM2FiNTA0ZjI1N2EiLCJjb2duaXRvOmdyb3VwcyI6WyJjbGllbnRlcyJdLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV8xSEFqSDFmS2oiLCJjbGllbnRfaWQiOiI3cWVwb28yOHNhbTlhaGJmdTNiZW1kajg0MyIsIm9yaWdpbl9qdGkiOiJkYzgyMDBhNy1lOWE3LTRiN2ItYjY2Yy05MmM5MDFhZGRkMTMiLCJldmVudF9pZCI6IjQwNTQzY2ZjLTI3YTUtNGE2ZC05OWZmLWE1ZTkwNjBiNGRjOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MTk2MDg4MDAsImV4cCI6MTcxOTYxMjQwMCwiaWF0IjoxNzE5NjA4ODAwLCJqdGkiOiIxNjk3NmM3MS02MjAxLTQ0YjEtYjZlYS0yMDYzMGU0OThhNDUiLCJ1c2VybmFtZSI6ImNsaWVudGUifQ.RDXTakFZKsz0Hv81XXgj86Iv6LCCQchJvDvcRqBZSSTZ9yHm2wVRA1Z0VNpLZGsgRDLxvyvZMpitlBn7cEi1rTvaM_lr0pZ4gPp50EZOwn8ngE3WxLOGZUCXSfH7qHtUmTcOUZjRjDKxL1JwY_V2aK_yRviQrIg66yGC8z3s1PtPycyyudh1jzK80IKir8HQmqNIgcv-BLR1uobcR1Ny5paO7b3Z_DtiYpVHA-Qz6GWhG7XSGNeI6G7JSfR_ZJ4oUMBOPS3xATvldaDfgQ7w1HB_8UmfnPR23gSo4v5rxNnGp5LyPM7UgMBngLMbGdC69CeMqteTaSPddgtbGdo21g'
        }),
        'body': json.dumps({
            'id': 3
        })
    }
    response = app.lambda_handler(evento, "")
    print(response)
