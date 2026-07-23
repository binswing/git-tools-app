a = {
    "addon":[
        {"a": "value1"},
        {"a": "value2"}
    ]
}
b = {
    "addon":[
        {"a": "value3"},
        {"a": "value4"},
        {"a": "value5"}
    ]
}
a.update(b)
print(a)