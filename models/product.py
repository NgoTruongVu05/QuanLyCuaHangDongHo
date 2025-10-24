class Product:
    def __init__(self, id=None, name="", brand="", product_type="", price=0.0, quantity=0, description=""):
        self.id = id
        self.name = name
        self.brand = brand
        self.product_type = product_type  # "mechanical" hoặc "electronic"
        self.price = price
        self.quantity = quantity
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'product_type': self.product_type,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            brand=data['brand'],
            product_type=data['product_type'],
            price=data['price'],
            quantity=data['quantity'],
            description=data['description']
        )

class MechanicalWatch(Product):
    def __init__(self, id=None, name="", brand="", price=0.0, quantity=0, description="", 
                 movement_type="", power_reserve=0, water_resistant=False):
        super().__init__(id, name, brand, "mechanical", price, quantity, description)
        self.movement_type = movement_type  # "automatic" hoặc "manual"
        self.power_reserve = power_reserve  # giờ
        self.water_resistant = water_resistant
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'movement_type': self.movement_type,
            'power_reserve': self.power_reserve,
            'water_resistant': self.water_resistant
        })
        return data

class ElectronicWatch(Product):
    def __init__(self, id=None, name="", brand="", price=0.0, quantity=0, description="",
                 battery_life=0, features=None, connectivity=""):
        super().__init__(id, name, brand, "electronic", price, quantity, description)
        self.battery_life = battery_life  # năm
        self.features = features or []  # ["heart_rate", "gps", ...]
        self.connectivity = connectivity  # "bluetooth", "wifi", "none"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'battery_life': self.battery_life,
            'features': ','.join(self.features) if self.features else '',
            'connectivity': self.connectivity
        })
        return data