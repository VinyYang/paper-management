from setuptools import setup, find_packages

setup(
    name="literature-management",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "alembic>=1.12.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "PyPDF2>=3.0.0",
        "numpy>=1.24.0",
        "redis>=4.5.0",
        "pydantic-settings>=2.0.0"
    ],
) 