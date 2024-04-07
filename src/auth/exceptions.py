from fastapi import HTTPException, status


token_invalid = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Token invalid",
)

token_expired = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
)

iam_teapot = HTTPException(
    status_code=status.HTTP_418_IM_A_TEAPOT,
    detail="I`m teapot",
)

wrong_login_password = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)

user_inactive = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User inactive",
)
