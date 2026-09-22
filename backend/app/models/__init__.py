# 模型包：集中导入所有模型
# 目的：只要 import 这个包，SQLAlchemy 的 Base.metadata 就能"知道"全部表，
# 这样 create_all 建表和模型之间的关联才能正常工作

from app.models.after_sales_order import AfterSalesItem, AfterSalesOrder, RepairRecord
from app.models.category import Category
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.payment_method import PaymentMethod
from app.models.product import Product
from app.models.product_price import ProductPrice
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.purchase_receipt import PurchaseReceipt, PurchaseReceiptItem
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.sales_shipment import SalesShipment, SalesShipmentItem
from app.models.serial_inventory import SerialInventory
from app.models.supplier import Supplier
from app.models.unit import Unit
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "AfterSalesItem",
    "AfterSalesOrder",
    "Category",
    "Customer",
    "Inventory",
    "PaymentMethod",
    "Product",
    "ProductPrice",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "PurchaseReceipt",
    "PurchaseReceiptItem",
    "RepairRecord",
    "Role",
    "RolePermission",
    "SalesOrder",
    "SalesOrderItem",
    "SalesShipment",
    "SalesShipmentItem",
    "SerialInventory",
    "Supplier",
    "Unit",
    "User",
    "Warehouse",
]