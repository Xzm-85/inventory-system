# 模型包：集中导入所有模型
# 目的：只要 import 这个包，SQLAlchemy 的 Base.metadata 就能"知道"全部表，
# 这样 create_all 建表和模型之间的关联才能正常工作

from app.models.category import Category
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.purchase_receipt import PurchaseReceipt, PurchaseReceiptItem
from app.models.supplier import Supplier
from app.models.unit import Unit
from app.models.warehouse import Warehouse

__all__ = [
    "Category",
    "Customer",
    "Inventory",
    "Product",
    "ProductPrice",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "PurchaseReceipt",
    "PurchaseReceiptItem",
    "Supplier",
    "Unit",
    "Warehouse",
]