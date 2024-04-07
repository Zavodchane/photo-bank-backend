from fastapi import HTTPException, status

invald_format = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid foto format")
