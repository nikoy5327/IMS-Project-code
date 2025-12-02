if __name__ == "__main__":

    from product_crud import product_crud
    from inventory_crud_pg import InventoryCRUD
    from sale_transaction import sale_transaction
    from sale_item import sale_item
    from decimal import Decimal
    from sale_transaction_crud import sale_transaction_crud as stc


    pc = product_crud("localhost",
                     "carols_ims",
                     "ims_user",
                     "password123")

    eggs = pc.search_product_sales("Eggs")
    rice = pc.search_product_sales("Rice")
    print("name:", eggs["name"], "price:", eggs["price"], "quantity:", eggs["current_quantity"])
    print("name:", rice["name"], "price:", rice["price"], "quantity:", rice["current_quantity"])
    print("-----")
    inventory_db = InventoryCRUD("localhost",
                    "carols_ims",
                    "ims_user",
                    "password123")
    sale_tx_db = stc("localhost",
                    "carols_ims",
                    "ims_user",
                    "password123")

    st = sale_transaction(Decimal("0.15"), Decimal("0.5") , inventory_db, pc, sale_tx_db)
    st.add_sale_item(eggs, 2)
    st.add_sale_item(rice, 1)

    for item in st.sale_items:
        print("Item:", item.product["name"], "Quantity:", item.quantity, "Price:", item.price)  


    #st.add_sale_item
    tx_data = st.calculate_transaction_data()
    print(tx_data)
    print("-----")
    cashier_id = 1
    st.finalize_transaction(cashier_id)
    
    eggs = pc.search_product_sales("Eggs")
    rice = pc.search_product_sales("Rice")
    print("name:", eggs["name"], "price:", eggs["price"], "quantity:", eggs["current_quantity"])
    print("name:", rice["name"], "price:", rice["price"], "quantity:", rice["current_quantity"])

    pass