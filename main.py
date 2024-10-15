from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session
from . import model

from .database import engine
from .database import get_db
import bcrypt
import os
salt = bcrypt.gensalt()

app = FastAPI()
model.Base.metadata.create_all(bind=engine)
from cryptography.fernet import Fernet
KEY_FILE = "encryption_key.key"


def load_key():
    """Load the encryption key from the key file."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        return generate_key()

def generate_key():
    return Fernet.generate_key()

def encrypt_password(key, password):
    fernet = Fernet(key)
    encrypted_bytes = fernet.encrypt(password.encode())  # Encrypts bytes
    return encrypted_bytes.decode('utf-8')

def decrypt_password(key, encrypted_password):
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

def generate_key():
    """Generate a new encryption key and save it to a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key


class password(BaseModel):  # helps us check if post contains the right type of data
    # otherwise it will throw an error
    Type: str
    Password: str

key = load_key()

@app.get("/")
def root():
    return {"message": "Welcome to PassGuard"}


@app.get("/pwmanager")
def get_posts(db: Session = Depends(get_db)):
    password_records = db.query(model.Password).all()
    if not password_records:
        raise HTTPException(status_code=404, detail="No passwords found")

    decrypted_records = []
    for record in password_records:
        try:
            decrypted_pw = decrypt_password(key, record.Password)
            decrypted_records.append({
                "Type": record.Type,
                "DecryptedPassword": decrypted_pw
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail="Password could not be decrypted")

    return {"data": decrypted_records}


# @app.get("/pwmanager/{id}")
# def get_posts(id, db: Session = Depends(get_db)):
#     db_item = db.query(model.Password).filter(model.Password.id == id).first()
#     if not db_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"password with id: {id} was not found")
#     return {"data": db_item}


@app.post("/pwmanager", status_code=status.HTTP_201_CREATED)
def create_pw(pw: password, db: Session = Depends(get_db)):
    encrypted_password = encrypt_password(key, pw.Password)  # Encrypt the password
    pw.Password = encrypted_password
    new_pw = model.Password(**pw.dict())

    db.add(new_pw)
    db.commit()
    db.refresh(new_pw)
    return {"data": new_pw}


# @app.put("/pwmanager/{id}")
# def update_pw(id, pw=password, db: Session = Depends(get_db)):
#     db_item = db.query(model.Password).filter(model.Password.id == id).first()
#     if db_item is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"pw with id: {id} does not exist")
#     db_item.Password = pw.Password
#     db.commit()
#     return {"data": db_item.Password}
#

@app.delete("/pwmanager/delete_all", status_code=status.HTTP_204_NO_CONTENT)
def delete_pw(db: Session = Depends(get_db)):
    db_item = db.query(model.Password).all()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"pw with id {id} does not exist")
    for item in db_item:
        db.delete(item)
        db.commit()
    return {Response(status_code=status.HTTP_204_NO_CONTENT)}
