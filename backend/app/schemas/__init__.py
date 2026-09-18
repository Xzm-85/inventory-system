# Schema 包：集中导出，其他文件可以直接 from app.schemas import Xxx

from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.inventory import AvailableSerialsResponse, Inventory, SerialInfo
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.schemas.product_price import ProductPrice, ProductPriceCreate
from app.schemas.purchase_order import (
    PurchaseOrder,
    PurchaseOrderCreate,
    PurchaseOrderItem,
    PurchaseOrderItemCreate,
    PurchaseOrderUpdate,
)
from app.schemas.purchase_receipt import (
    PurchaseReceipt,
    PurchaseReceiptCreate,
    PurchaseReceiptItem,
    PurchaseReceiptItemCreate,
)
from app.schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from app.schemas.unit import Unit, UnitCreate, UnitUpdate
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseUpdate

__all__ = [
    "Category",
    "CategoryCreate",
    "CategoryUpdate",
    "Customer",
    "CustomerCreate",
    "CustomerUpdate",
    "Inventory",
    "AvailableSerialsResponse",
    "SerialInfo",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductPrice",
    "ProductPriceCreate",
    "PurchaseOrder",
    "PurchaseOrderCreate",
    "PurchaseOrderItem",
    "PurchaseOrderItemCreate",
    "PurchaseOrderUpdate",
    "PurchaseReceipt",
    "PurchaseReceiptCreate",
    "PurchaseReceiptItem",
    "PurchaseReceiptItemCreate",
    "Supplier",
    "SupplierCreate",
    "SupplierUpdate",
    "Unit",
    "UnitCreate",
    "UnitUpdate",
    "Warehouse",
    "WarehouseCreate",
    "WarehouseUpdate",
]