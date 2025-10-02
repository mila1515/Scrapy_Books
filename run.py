if __name__ == "__main__":
    import uvicorn
    from books_api.presentation.main import app
    uvicorn.run("books_api.presentation.main:app", host="0.0.0.0", port=8000, reload=True)
