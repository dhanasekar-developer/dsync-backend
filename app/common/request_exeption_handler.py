from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

error_messages = {
    'email': 'Please enter valid email address!',
    'new_password': 'Password should be at least 8 character!'
}

def register_exeption_handler(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def request_exeption_handler(request: Request, exc: RequestValidationError):
        
        first_error = exc.errors()[0]

        field = first_error['loc'][-1]

        if error_messages.get(field, None):
            msg = error_messages[field]

        else:
            msg = first_error['msg']

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                'success': False,
                'field': field,
                'message': msg
            }
        )