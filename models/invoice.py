from datetime import datetime

class Invoice:
    def __init__(self, id=None, customer_id=None, employee_id=None, total_amount=0.0, 
                 created_date=None, invoice_type="sale", status="pending"):
        self.id = id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.total_amount = total_amount
        self.created_date = created_date or datetime.now().strftime('%Y-%m-%d')
        self.invoice_type = invoice_type  # "sale" hoặc "repair"
        self.status = status  # "pending", "completed", "cancelled"
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'employee_id': self.employee_id,
            'total_amount': self.total_amount,
            'created_date': self.created_date,
            'invoice_type': self.invoice_type,
            'status': self.status
        }

class InvoiceDetail:
    def __init__(self, id=None, invoice_id=None, product_id=None, quantity=0, price=0.0):
        self.id = id
        self.invoice_id = invoice_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }

class RepairOrder:
    def __init__(self, id=None, customer_id=None, employee_id=None, watch_description="", 
                 issue_description="", estimated_cost=0.0, actual_cost=0.0,
                 created_date=None, estimated_completion=None, status="pending"):
        self.id = id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.watch_description = watch_description
        self.issue_description = issue_description
        self.estimated_cost = estimated_cost
        self.actual_cost = actual_cost
        self.created_date = created_date or datetime.now().strftime('%Y-%m-%d')
        self.estimated_completion = estimated_completion
        self.status = status  # "pending", "in_progress", "completed", "cancelled"
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'employee_id': self.employee_id,
            'watch_description': self.watch_description,
            'issue_description': self.issue_description,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'created_date': self.created_date,
            'estimated_completion': self.estimated_completion,
            'status': self.status
        }