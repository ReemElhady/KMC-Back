def return_cart_summary(total_price, tax, discount_percentage=0):
    data = {
        "total_price": total_price,
        "tax": 0,
        "sub_total": 0,
        "discount": 0,
    }

    if tax and total_price:
        data["tax"] = round(total_price * (tax / 100), 2)
    if discount_percentage and total_price:
        data["discount"] = round((discount_percentage / 100) * total_price, 2)
        data["total_price"] = data["total_price"] - data["discount"]
    if data["tax"] and total_price:
        data["sub_total"] = round(total_price - data.get("tax"), 2)

    return data
