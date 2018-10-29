""" Script to sort a list of touples based on the second item of the touple (dates). From older date to newer"""

import datetime

orders = {
    '1668714ec93ba065': [
        ('166873001e44b485', datetime.datetime(2018, 10, 18, 12, 39, 5, tzinfo=datetime.timezone.utc)),
        ('1668714ec93ba065', datetime.datetime(2018, 10, 18, 12, 9, 37, tzinfo=datetime.timezone.utc)),
        ('1668730309c95aba', datetime.datetime(2018, 10, 18, 12, 39, 26, tzinfo=datetime.timezone.utc))
    ],
    '166872ffde8c27c6': [
        ('166872ffde8c27c6', datetime.datetime(2018, 10, 18, 12, 39, 15, tzinfo=datetime.timezone.utc))
    ],
    '16669d0e7c1ded90': [
        ('166825c24bec9aca', datetime.datetime(2018, 10, 17, 14, 9, 15, tzinfo=datetime.timezone.utc)),
        ('1668263fc44b45db', datetime.datetime(2018, 10, 17, 14, 17, 50, tzinfo=datetime.timezone.utc)),
        ('166826d0c38d62da', datetime.datetime(2018, 10, 17, 14, 27, 43, tzinfo=datetime.timezone.utc)),
        ('16682a76af7ae2cf', datetime.datetime(2018, 10, 17, 15, 31, 27, tzinfo=datetime.timezone.utc)),
        ('16669d0e7c1ded90', datetime.datetime(2018, 10, 12, 19, 46, 20, tzinfo=datetime.timezone.utc)),
        ('16669dcaeb9ea531', datetime.datetime(2018, 10, 12, 15, 59, 6, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('16669defdbedffae', datetime.datetime(2018, 10, 12, 20, 1, 46, tzinfo=datetime.timezone.utc)),
        ('16669eb99842fb96', datetime.datetime(2018, 10, 12, 16, 15, 25, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('1666a0164cc4b1a3', datetime.datetime(2018, 10, 12, 20, 39, 20, tzinfo=datetime.timezone.utc)),
        ('1666a0c96dfa39f7', datetime.datetime(2018, 10, 12, 16, 51, 25, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('1666dfcbbfcbbc8e', datetime.datetime(2018, 10, 13, 11, 12, 36, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('1666e1339438bab3', datetime.datetime(2018, 10, 13, 11, 37, 8, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('166821ec5b594fbe', datetime.datetime(2018, 10, 17, 13, 2, 11, tzinfo=datetime.timezone.utc)),
        ('16682ac45249277f', datetime.datetime(2018, 10, 17, 15, 36, 46, tzinfo=datetime.timezone.utc))
    ],
    '1667ff8de74e9ad9': [
        ('1667ff8de74e9ad9', datetime.datetime(2018, 10, 17, 3, 1, 30, tzinfo=datetime.timezone.utc))
    ],
    '166790b0d778508a': [
        ('166790b0d778508a', datetime.datetime(2018, 10, 15, 18, 44, 2, tzinfo=datetime.timezone.utc))
    ],
    '166778305e83c856': [
        ('166785ac70ca6d2c', datetime.datetime(2018, 10, 15, 15, 31, 32, tzinfo=datetime.timezone.utc))
    ],
    '1667840451331339': [
        ('1667840451331339', datetime.datetime(2018, 10, 15, 15, 2, 39, tzinfo=datetime.timezone.utc))
    ],
    '1666e2a01aeaab79': [
        ('1666ec3f51129ca6', datetime.datetime(2018, 10, 13, 18, 50, 20, tzinfo=datetime.timezone.utc)),
        ('1667316cade019b4', datetime.datetime(2018, 10, 14, 14, 59, 7, tzinfo=datetime.timezone.utc)),
        ('16673184a5f590cf', datetime.datetime(2018, 10, 14, 11, 0, 49, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('1666e2a01aeaab79', datetime.datetime(2018, 10, 13, 16, 2, 4, tzinfo=datetime.timezone.utc)),
        ('1666e2be3ba55896', datetime.datetime(2018, 10, 13, 12, 4, 7, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('1666ebf2567bbb3f', datetime.datetime(2018, 10, 13, 14, 44, 59, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000)))),
        ('16673264f3645cd3', datetime.datetime(2018, 10, 14, 15, 16, 11, tzinfo=datetime.timezone.utc)),
        ('166732819b075a9e', datetime.datetime(2018, 10, 14, 11, 18, 3, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000))))
    ]
}

print(orders)
sorted_orders = {}

for key, value in orders.items():
    print(key)
    print(value)
    sorted_orders[key] = sorted(value, key=lambda x: x[-1])
    print(sorted_orders[key])
