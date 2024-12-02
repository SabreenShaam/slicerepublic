def calculate_drop_in_transfer_price(drop_in_price):
    drop_in = round((drop_in_price * 60) / 100, 2)
    return drop_in


def calculate_ten_pack_transfer_price(ten_pack_price):
    ten_pack = round((ten_pack_price * 75) / 100, 2)
    return ten_pack


def calculate_transfer_price(drop_in_transfer, ten_pack_transfer):
    return min(drop_in_transfer, ten_pack_transfer)
