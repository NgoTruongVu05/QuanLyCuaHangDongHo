class Employee:
    def __init__(self, id=None, username="", password="", full_name="", role=0, 
                 phone="", email="", base_salary=0.0, position=""):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role  # 0: nhân viên, 1: quản lý
        self.phone = phone
        self.email = email
        self.base_salary = base_salary
        self.position = position  # "sales", "technician", "manager"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'full_name': self.full_name,
            'role': self.role,
            'phone': self.phone,
            'email': self.email,
            'base_salary': self.base_salary,
            'position': self.position
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            username=data['username'],
            password=data['password'],
            full_name=data['full_name'],
            role=data['role'],
            phone=data['phone'],
            email=data['email'],
            base_salary=data['base_salary'],
            position=data['position']
        )