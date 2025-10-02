from setuptools import setup, find_packages

setup(
    name="books_api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-dotenv"
    ]
)
