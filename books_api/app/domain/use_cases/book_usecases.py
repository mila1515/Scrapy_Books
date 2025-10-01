from typing import List
from app.domain.models import Book
from app.data.repositories.book_repository import BookRepository

class BookUseCases:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def list_books(self) -> List[Book]:
        return self.repo.get_all_books()

    def get_book_by_id(self, book_id: int) -> Book:
        return self.repo.get_book(book_id)
        
    def search_books_by_title(self, title: str) -> List[Book]:
        return self.repo.search_books_by_title(title)
        
    def search_books_by_category(self, category: str) -> List[Book]:
        return self.repo.search_books_by_category(category)
