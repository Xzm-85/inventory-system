# Schema 包：集中导出，其他文件可以直接 from app.schemas import Xxx

from app.schemas.after_sales import (
    AFTER_SALES_STATUSES,
    AFTER_SALES_TYPES,
    AfterSales,
    AfterSalesCreate,
    AfterSalesItem,
    AfterSalesItemCreate,
    AfterSalesStatusUpdate,
)
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.inventory import AvailableSerialsResponse, Inventory, SerialInfo
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.schemas.product_price import ProductPrice, ProductPriceCreate
from app.schemas.payment_method import PaymentMethod, PaymentMethodCreate, PaymentMethodUpdate
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
from app.schemas.repair_record import (
    REPAIR_STATUSES,
    RepairRecord,
    RepairRecordCreate,
    RepairRecordUpdate,
)
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.role_permission import (
    PERMISSION_MODULES,
    RolePermission,
    RolePermissionBatch,
    RolePermissionItem,
)
from app.schemas.sales_order import (
    SalesOrder,
    SalesOrderCreate,
    SalesOrderItem,
    SalesOrderItemCreate,
)
from app.schemas.sales_shipment import (
    SalesShipment,
    SalesShipmentCreate,
    SalesShipmentItem,
    SalesShipmentItemCreate,
)
from app.schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from app.schemas.unit import Unit, UnitCreate, UnitUpdate
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseUpdate

__all__ = [
    "AFTER_SALES_STATUSES",
    "AFTER_SALES_TYPES",
    "AfterSales",
    "AfterSalesCreate",
    "AfterSalesItem",
    "AfterSalesItemCreate",
    "AfterSalesStatusUpdate",
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
    "PaymentMethod",
    "PaymentMethodCreate",
    "PaymentMethodUpdate",
    "PurchaseOrder",
    "PurchaseOrderCreate",
    "PurchaseOrderItem",
    "PurchaseOrderItemCreate",
    "PurchaseOrderUpdate",
    "PurchaseReceipt",
    "PurchaseReceiptCreate",
    "PurchaseReceiptItem",
    "PurchaseReceiptItemCreate",
    "REPAIR_STATUSES",
    "RepairRecord",
    "RepairRecordCreate",
    "RepairRecordUpdate",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "PERMISSION_MODULES",
    "RolePermission",
    "RolePermissionBatch",
    "RolePermissionItem",
    "SalesOrder",
    "SalesOrderCreate",
    "SalesOrderItem",
    "SalesOrderItemCreate",
    "SalesShipment",
    "SalesShipmentCreate",
    "SalesShipmentItem",
    "SalesShipmentItemCreate",
    "Supplier",
    "SupplierCreate",
    "SupplierUpdate",
    "Unit",
    "UnitCreate",
    "UnitUpdate",
    "User",
    "UserCreate",
    "UserUpdate",
    "Warehouse",
    "WarehouseCreate",
    "WarehouseUpdate",
]