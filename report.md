

![image-20241017133532822](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20241017133532822.png

![image-20241016211652295](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20241016211652295.png)



user表：

主键为user_id，

| user_id                            | password                           | balance                            | token                                                | terminal                           |
| ---------------------------------- | ---------------------------------- | ---------------------------------- | ---------------------------------------------------- | ---------------------------------- |
| 类型string，描述：用户名，不可为空 | 类型string，描述：用户名，不可为空 | 类型string，描述：用户名，不可为空 | 类型string,user_id和terminal与时间戳的加密连接字符串 | 类型string，描述：用户名，不可为空 |



user_store表：

主键为store_id (note:一个用户可能拥有多个store)

| store_id                     | user_id |
| ---------------------------- | ------- |
| string类型，描述：商店标识符 |         |



store表：

主键为(store_id)

| store_id | book_ids | stock_level             |
| -------- | -------- | ----------------------- |
|          |          | 对应store的book的存储量 |

```
{
  "store_id": "store_1",
  "book_stock_info": [
    { "book_id": "book_1", "stock_level": 10 },
    { "book_id": "book_2", "stock_level": 5 }
  ]
}
```



book表

| book_id | book_info(可以继续转换) |
| ------- | ----------------------- |
|         | string类型，由json转换  |

该表设立的假设，每个book仅有一个id，即同一本书，在不同的store中，其id相同。

符合该假设的现实场景为：商店添加书本，将书本信息提交到售书平台,由售书平台分发一个ID，记录书本信息到平台的数据库内，然后返回ID给商家。



new_order表：

主键为（order_id）

| order_id | user_id | store_id | books_status | create_time |
| -------- | ------- | -------- | ------ | ------ |
|          |         |          |        |        |



| status code | status         |
| ----------- | -------------- |
| -1          | 取消           |
| 0           | 已发货，未收货         |
| 1           | 已付款,待发货         |
| 2           | 初始值，未付款 |
| 3           | 已收货         |



new_order_detail表：

| order_id                         | book_id | count | price |
| -------------------------------- | ------- | ----- | ----- |
| 主键为联合主键(order_id,book_id) |         |       |       |

