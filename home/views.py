from django.http import HttpResponse


# Hardcoded sample order data
ORDERS = [
    {"order_id": "ORD-001", "product": "Ergonomic Office Chair",      "customer": "Alice Johnson"},
    {"order_id": "ORD-002", "product": "Standing Desk (Walnut)",       "customer": "Bob Martinez"},
    {"order_id": "ORD-003", "product": "Mechanical Keyboard",          "customer": "Clara Singh"},
    {"order_id": "ORD-004", "product": "27\" 4K Monitor",              "customer": "David Kim"},
    {"order_id": "ORD-005", "product": "Noise-Cancelling Headphones",  "customer": "Eva Patel"},
    {"order_id": "ORD-006", "product": "Webcam HD 1080p",              "customer": "Frank Osei"},
    {"order_id": "ORD-007", "product": "USB-C Docking Station",        "customer": "Grace Liu"},
    {"order_id": "ORD-008", "product": "Laptop Stand (Aluminium)",     "customer": "Henry Brown"},
    {"order_id": "ORD-009", "product": "Wireless Mouse",               "customer": "Irene Torres"},
    {"order_id": "ORD-010", "product": "LED Desk Lamp",                "customer": "James Nguyen"},
    {"order_id": "ORD-011", "product": "Cable Management Kit",         "customer": "Karen White"},
    {"order_id": "ORD-012", "product": "Mesh Wi-Fi Router",            "customer": "Liam Scott"},
]


def index(request):
    total_orders = len(ORDERS)

    # Build table rows
    rows_html = ""
    for order in ORDERS:
        rows_html += f"""
            <tr>
                <td>
                    <span class="tip-tag tip-tag-primary">{order['order_id']}</span>
                </td>
                <td>{order['product']}</td>
                <td>{order['customer']}</td>
                <td>
                    <div style="display:flex;gap:8px;">
                        <button class="tip-btn tip-btn-outline" style="padding:4px 12px;font-size:13px;">View</button>
                        <button class="tip-btn tip-btn-ghost"   style="padding:4px 12px;font-size:13px;">Edit</button>
                    </div>
                </td>
            </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orders — TriangleIP</title>
    <link rel='stylesheet' href='/static/tip_design.css'>
    <style>
        /* subtle page-level tweaks — no colour hard-codes */
        .orders-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .tip-table tbody tr:hover {{
            background: var(--tip-bg-alt, #f9fafb);
        }}
        .tip-table td, .tip-table th {{
            vertical-align: middle;
        }}
    </style>
</head>
<body>

<!-- ── Navbar ─────────────────────────────────────────────── -->
<nav class="tip-navbar">
    <a class="tip-navbar-brand" href="/">
        &#9651;&nbsp; TriangleIP
    </a>
    <div style="display:flex;gap:8px;">
        <button class="tip-btn tip-btn-ghost">Dashboard</button>
        <button class="tip-btn tip-btn-ghost">Reports</button>
    </div>
</nav>

<!-- ── Main content ───────────────────────────────────────── -->
<div class="tip-page">

    <!-- Page title -->
    <h1 class="tip-page-title">Orders</h1>

    <!-- Stats row -->
    <div class="tip-stats-row">
        <div class="tip-card" style="flex:1;min-width:160px;">
            <div style="color:var(--tip-text-secondary);font-size:13px;margin-bottom:4px;">Total Orders</div>
            <div class="tip-card-value">{total_orders}</div>
        </div>
        <div class="tip-card" style="flex:1;min-width:160px;">
            <div style="color:var(--tip-text-secondary);font-size:13px;margin-bottom:4px;">Pending</div>
            <div class="tip-card-value">4</div>
        </div>
        <div class="tip-card" style="flex:1;min-width:160px;">
            <div style="color:var(--tip-text-secondary);font-size:13px;margin-bottom:4px;">Shipped</div>
            <div class="tip-card-value">6</div>
        </div>
        <div class="tip-card" style="flex:1;min-width:160px;">
            <div style="color:var(--tip-text-secondary);font-size:13px;margin-bottom:4px;">Delivered</div>
            <div class="tip-card-value">2</div>
        </div>
    </div>

    <!-- Orders card + table -->
    <div class="tip-card" style="margin-top:28px;padding:0;">

        <!-- Card header -->
        <div class="orders-header" style="padding:20px 24px 0 24px;">
            <div>
                <h2 style="margin:0;font-size:18px;font-weight:600;">Order List</h2>
                <p style="margin:4px 0 0;color:var(--tip-text-secondary);font-size:13px;">
                    All customer orders — {total_orders} records
                </p>
            </div>
            <button class="tip-btn tip-btn-primary">+ New Order</button>
        </div>

        <div style="height:16px;"></div>

        <!-- Table -->
        <div class="tip-table-wrap">
            <table class="tip-table">
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Product</th>
                        <th>Customer</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>

    </div><!-- /tip-card -->

</div><!-- /tip-page -->

</body>
</html>"""

    return HttpResponse(html, content_type="text/html")
