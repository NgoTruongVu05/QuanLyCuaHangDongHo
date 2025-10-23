class Customer:
    def __init__(self, id=None, name="", phone="", email="", address=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            address=data['address']
        )