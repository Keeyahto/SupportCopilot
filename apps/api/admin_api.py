import os
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:5432/support")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_orders(status: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Получить список заказов с фильтрацией"""
    with engine.connect() as conn:
        query = """
        SELECT 
            o.id,
            o.order_no,
            o.created_at,
            o.status,
            o.total,
            c.email as customer_email,
            c.city as customer_city,
            COUNT(oi.id) as items_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        """
        
        params = {}
        if status:
            query += " WHERE o.status = :status"
            params["status"] = status
            
        query += """
        GROUP BY o.id, o.order_no, o.created_at, o.status, o.total, c.email, c.city
        ORDER BY o.created_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        params.update({"limit": limit, "offset": offset})
        
        result = conn.execute(text(query), params)
        orders = []
        for row in result:
            orders.append({
                "id": row.id,
                "order_no": row.order_no,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "status": row.status,
                "total": float(row.total) if row.total else 0,
                "customer_email": row.customer_email,
                "customer_city": row.customer_city,
                "items_count": row.items_count
            })
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM orders"
        if status:
            count_query += " WHERE status = :status"
        count_result = conn.execute(text(count_query), {"status": status} if status else {})
        total = count_result.scalar()
        
        return {
            "orders": orders,
            "total": total,
            "limit": limit,
            "offset": offset
        }


def get_order(order_id: int) -> Dict[str, Any]:
    """Получить детали заказа"""
    with engine.connect() as conn:
        # Get order details
        order_query = """
        SELECT 
            o.id,
            o.order_no,
            o.created_at,
            o.status,
            o.total,
            c.email as customer_email,
            c.city as customer_city,
            c.zip as customer_zip
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = :order_id
        """
        
        order_result = conn.execute(text(order_query), {"order_id": order_id})
        order_row = order_result.fetchone()
        
        if not order_row:
            return {"error": "Order not found"}
        
        # Get order items
        items_query = """
        SELECT 
            oi.id,
            oi.qty,
            oi.price,
            p.sku,
            p.name,
            p.category
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = :order_id
        """
        
        items_result = conn.execute(text(items_query), {"order_id": order_id})
        items = []
        for row in items_result:
            items.append({
                "id": row.id,
                "qty": row.qty,
                "price": float(row.price) if row.price else 0,
                "sku": row.sku,
                "name": row.name,
                "category": row.category
            })
        
        return {
            "id": order_row.id,
            "order_no": order_row.order_no,
            "created_at": order_row.created_at.isoformat() if order_row.created_at else None,
            "status": order_row.status,
            "total": float(order_row.total) if order_row.total else 0,
            "customer_email": order_row.customer_email,
            "customer_city": order_row.customer_city,
            "customer_zip": order_row.customer_zip,
            "items": items
        }


def update_order(order_id: int, request: Dict[str, Any]) -> Dict[str, Any]:
    """Обновить заказ"""
    with engine.connect() as conn:
        # Check if order exists
        check_query = "SELECT id FROM orders WHERE id = :order_id"
        check_result = conn.execute(text(check_query), {"order_id": order_id})
        if not check_result.fetchone():
            return {"error": "Order not found"}
        
        # Update order
        update_query = "UPDATE orders SET status = :status WHERE id = :order_id"
        conn.execute(text(update_query), {
            "status": request.get("status"),
            "order_id": order_id
        })
        conn.commit()
        
        return {"success": True, "message": "Order updated"}


def get_customers(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Получить список клиентов"""
    with engine.connect() as conn:
        query = """
        SELECT 
            c.id,
            c.email,
            c.city,
            c.zip,
            COUNT(o.id) as orders_count,
            COALESCE(SUM(o.total), 0) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.email, c.city, c.zip
        ORDER BY c.id
        LIMIT :limit OFFSET :offset
        """
        
        result = conn.execute(text(query), {"limit": limit, "offset": offset})
        customers = []
        for row in result:
            customers.append({
                "id": row.id,
                "email": row.email,
                "city": row.city,
                "zip": row.zip,
                "orders_count": row.orders_count,
                "total_spent": float(row.total_spent) if row.total_spent else 0
            })
        
        # Get total count
        count_result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        total = count_result.scalar()
        
        return {
            "customers": customers,
            "total": total,
            "limit": limit,
            "offset": offset
        }


def get_products(category: Optional[str] = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Получить список продуктов"""
    with engine.connect() as conn:
        query = """
        SELECT 
            p.id,
            p.sku,
            p.name,
            p.category,
            p.price,
            p.active,
            COUNT(oi.id) as orders_count
        FROM products p
        LEFT JOIN order_items oi ON p.id = oi.product_id
        """
        
        params = {}
        if category:
            query += " WHERE p.category = :category"
            params["category"] = category
            
        query += """
        GROUP BY p.id, p.sku, p.name, p.category, p.price, p.active
        ORDER BY p.id
        LIMIT :limit OFFSET :offset
        """
        
        params.update({"limit": limit, "offset": offset})
        
        result = conn.execute(text(query), params)
        products = []
        for row in result:
            products.append({
                "id": row.id,
                "sku": row.sku,
                "name": row.name,
                "category": row.category,
                "price": float(row.price) if row.price else 0,
                "active": row.active,
                "orders_count": row.orders_count
            })
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM products"
        if category:
            count_query += " WHERE category = :category"
        count_result = conn.execute(text(count_query), {"category": category} if category else {})
        total = count_result.scalar()
        
        return {
            "products": products,
            "total": total,
            "limit": limit,
            "offset": offset
        }


def get_admin_stats() -> Dict[str, Any]:
    """Получить статистику для админ-панели"""
    with engine.connect() as conn:
        # Total orders
        total_orders = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        
        # Orders by status
        status_stats = conn.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM orders 
            GROUP BY status
        """)).fetchall()
        
        # Total revenue
        total_revenue = conn.execute(text("SELECT COALESCE(SUM(total), 0) FROM orders")).scalar()
        
        # Orders today
        orders_today = conn.execute(text("""
            SELECT COUNT(*) FROM orders 
            WHERE DATE(created_at) = CURRENT_DATE
        """)).scalar()
        
        # Top products
        top_products = conn.execute(text("""
            SELECT p.name, p.sku, COUNT(oi.id) as orders_count
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            GROUP BY p.id, p.name, p.sku
            ORDER BY orders_count DESC
            LIMIT 5
        """)).fetchall()
        
        # Recent orders
        recent_orders = conn.execute(text("""
            SELECT o.order_no, o.status, o.total, c.email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.created_at DESC
            LIMIT 5
        """)).fetchall()
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue) if total_revenue else 0,
            "orders_today": orders_today,
            "orders_by_status": {row.status: row.count for row in status_stats},
            "top_products": [
                {
                    "name": row.name,
                    "sku": row.sku,
                    "orders_count": row.orders_count
                } for row in top_products
            ],
            "recent_orders": [
                {
                    "order_no": row.order_no,
                    "status": row.status,
                    "total": float(row.total) if row.total else 0,
                    "customer_email": row.email
                } for row in recent_orders
            ]
        }
