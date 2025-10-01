class Book:
    def __init__(self, id: int, title: str, author: str = None, category: str = None, 
                 price: float = 0.0, stock: int = 0, created_at: str = None, 
                 rating: int = None, url: str = None):
        self.id = id
        self.title = title
        self.author = author  # Champ non utilisé dans la base actuelle
        self.category = category
        self.price = price
        self.stock = stock
        self.created_at = created_at
        self.rating = rating
        self.url = url
