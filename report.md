

## 实验的功能和要求

- 实现一个提供网上购书功能的网站后端。<br>

- 网站支持书商在上面开商店，购买者可以通过网站购买。<br>
- 买家和卖家都可以注册自己的账号。<br>
- 一个卖家可以开一个或多个网上商店。
- 买家可以为自已的账户充值，在任意商店购买图书。<br>
- 支持 下单->付款->发货->收货 流程。<br>

**1.实现对应接口的功能，见项目的 doc 文件夹下面的 .md 文件描述 （60%）<br>**

其中包括：

1)用户权限接口，如注册、登录、登出、注销<br>

2)买家用户接口，如充值、下单、付款<br>

3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br>

通过对应的功能测试，所有 test case 都 pass <br>

**2.为项目添加其它功能 ：（40%）**

1)实现后续的流程 ：发货 -> 收货

2)搜索图书 ：用户可以通过关键字搜索，参数化的搜索方式；如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。如果显示结果较大，需要分页。(使用全文索引优化查找)

3)订单状态，订单查询和取消订单：用户可以查自已的历史订单，用户也可以取消订单。取消订单可由买家主动地取消，或者买家下单后，经过一段时间超时仍未付款，订单也会自动取消。 



具体的一些要求： 

1.`bookstore` 文件夹是该项目的 demo，采用 Flask 后端框架，实现了前60%功能以及对应的测试 用例代码。要求大家创建本地 `MongoDB 数据库`，将 `bookstore/fe/data/book.db` 中的内容以合适的形式存入本地数据库(在`bookstore/transfer_data.py`文件内实现)，后续所有数据读写都在本地的 MongoDB 数据库中进行。书本的内容可自行构造一批，也可参从网 盘下载，下载地址为：（https://pan.baidu.com/s/1bjCOW8Z5N_ClcqU54Pdt8g）提取码：hj6q 

2.在完成前60%功能的基础上，继续实现后40%功能，要有接口、后端逻辑实现、数据库操作、代码测试。对所有 接口都要写 test case，通过测试并计算测试覆盖率（尽量提高测试覆盖率）。

 3.尽量使用索引，对程序与数据库执行的性能有考量

 4.尽量使用 git 等版本管理工具

 5.不需要实现界面，只需通过代码测试体现功能与正确性



## 文档数据库的设计



**文档集合描述：**

------

**用户集合 (user)**

- `user_id`: 用户名
- `password`: 密码
- `balance`: 用户账户余额
- `token`: 加密标识符，由user_id和terminal与时间戳的加密连接字符串组成
- `terminal`: 登录终端信息
- 每个用户可能拥有多个商店，表示为子集合 `stores`

**主键**：`user_id`

------

**商店店家个人信息集合(user_store)**

- store_id:商店标识符
- user_id：用户名

**主键**：`store_id`

------

**商店集合 (store)**

- `store_id`: 商店标识符
- `book_stock_info`: 书本库存信息（数组结构）
  - 每个书本库存信息包含 `book_id` 和 `stock_level`

**主键：**`store_id`

------

**书本集合 (book)**

- `book_id`: 书本标识符
- `book_info`: 书本详细信息，通常为 JSON 格式

**主键**：`book_id`

------

**订单集合 (new_order)**

- `order_id`: 订单标识符
- `user_id`: 关联用户 ID
- `store_id`: 关联商店 ID
- `books_status`: 订单状态
- `create_time`: 创建时间

**主键**：`order_id`

**状态代码（books_status）：**

- -1: 取消
- 0: 已发货，未收货
- 1: 已付款，待发货
- 2: 初始值，未付款
- 3: 已收货

------

**订单详情集合 (new_order_detail)**

- `order_id`: 订单标识符（与 Orders 集合的 `order_id` 一致）
- `each_book_details`:一个订单内购买的书本的信息(数组结构)
  - `book_id`: 书本标识符
  - `count`: 订购数量
  - `price`: 单价

**主键：**`order_id`

------

**数据库结构设计理由：**

1.尽可能减少**降低读放大**。

在原来的关系型数据库的store表内，其数据如下 "INSERT into store(store_id, book_id, book_info, stock_level)"，这里的book_info表示了每本书的详细信息。而在查询一个store内是否包含某一book_id时，会不可避免的读取book_info这一信息,因此我们将book的信息单独形成一个集合，后续通过book_id查找书本的具体信息。这一样在**降低读放大**的同时，也可以有效的降低b+树叶子结点的数量，降低高度，使得**查询更快**。也更好的实现了解耦合，可以方便的从外部查找某一书本的信息。

2.根据数据库特性改变结构：

由于之前的数据库是关系型数据库，这就导致无法在一个字段内存储数组信息，例如`INSERT INTO new_order_detail(order_id, book_id, count, price) `,需要重复的order_id，来记录本次订单内的某一书本的详细信息。此外还有一个好处是，原先的设计模式因为重复的`order_id`，其索引是`order_id, book_id`的组合。而现在索引只需要在`order_id`上设置索引即可。并且，按照实际情况单次order内的book种类不会过多。因此若要其对某一`order_id, book_id`的查找所增加的线性开销其影响是有限的。

3.增加可扩展性

```
(user_store)
- store_id:商店标识符
- user_id：用户名
**商店集合 (store)**
- `store_id`: 商店标识符
- `book_stock_info`: 书本库存信息（数组结构）
  - 每个书本库存信息包含 `book_id` 和 `stock_level`
```

这里我们保留了user_store表。之所以不将user_id放入stroe集合，是因这会方便后续对于某一商店的用户信息进行相关调研，例如经济情况(balance).并且因为一个用户可能拥有多个store，若要根据user_id来对其所拥有的所有商户进行分析，这种设计方式可以仅仅通过少量的冗余信息，加快查找速度。

4.索引设计

采用索引对于“频繁查找，不常更改”的数据项之查找功能来说起到了十分好的性能增益作用。我们在每个文档集合的ID字段上设置了索引(即主键). 为了允许对文本字段进行全文搜索，books文档集上设置了多个索引，分别是在字段 title,tags,book_intro,content上（这些字段的内容都是文本，所以类型都设置为了text）。



## 基本功能实现

### 用户注册与注销（`register`, `unregister`）

**`register` 函数**

- **参数**：
  - `user_id`：要注册的用户ID。
  - `password`：用户的密码。
- **返回值**：
  - 一个元组，包含以下两个元素：
    - 一个整数：表示操作的状态码，`200` 表示成功，`528` 表示发生某种错误。
    - 一个字符串：描述操作结果，通常是消息或错误信息。
- **主要流程**：
  1. 尝试生成一个唯一的终端标识，格式为 `"terminal_<当前时间戳>"`。
  2. 使用 `jwt_encode` 函数，基于用户提供的 `user_id` 和生成的终端标识生成一个 `token`。
  3. 将用户信息插入数据库的 `user` 集合中，字段包括 `user_id`、`password`、`balance`、`token` 和 `terminal`。
  4. 如果在上述过程中发生异常，函数会捕获并返回状态码 `528` 和异常的字符串表示作为错误消息。
  5. 操作成功时，返回状态码 `200` 和消息 `"ok"`。

**`unregister` 函数**

- **参数**：
  - `user_id`：要注销的用户ID。
  - `password`：用户的密码。
- **返回值**：
  - 一个元组，包含以下两个元素：
    - 一个整数：表示操作的状态码，`200` 表示成功，`530` 表示发生异常，以及其他可能的状态码。
    - 一个字符串：描述操作结果，通常是消息或错误信息。
- **主要流程**：
  1. 调用 `check_password` 方法，验证用户输入的 `user_id` 和 `password` 是否正确。
  2. 如果密码验证不通过，返回错误状态码和相应的错误消息。
  3. 成功通过验证后，从数据库 `user` 集合中删除对应的 `user_id` 记录。
  4. 如果在过程中发生异常，函数会捕获并返回状态码 `528` 或 `530`，附带异常的字符串描述作为错误消息。
  5. 操作成功时，返回状态码 `200` 和消息 `"ok"`。

### 用户登入和登出

**`login` 函数**

- **参数**：
  - `user_id`：用户的ID。
  - `password`：用户的密码。
  - `terminal`：终端标识符。
- **返回值**：
  - 一个元组，包含以下三个元素：
    - 一个整数：表示状态码，`200` 表示登录成功，其他状态码表示错误。
    - 一个字符串：描述操作结果的消息或错误消息。
    - 一个字符串：表示生成的 `token`，失败时返回空字符串。
- **主要流程**：
  1. 调用 `check_password` 验证 `user_id` 和 `password`。
  2. 若验证失败，返回错误状态码和消息。
  3. 若验证成功，生成新的 `token` 并更新 `user` 集合中该用户的 `token` 和 `terminal` 字段。
  4. 如果更新失败，返回授权失败的状态码和消息。
  5. 若操作成功，返回状态码 `200`、消息 `"ok"` 和生成的 `token`。

**`logout` 函数**

- **参数**：
  - `user_id`：用户的ID。
  - `token`：用户的登录令牌。
- **返回值**：
  - 一个元组，包含以下两个元素：
    - 一个整数：表示状态码，`200` 表示登出成功，其他状态码表示错误。
    - 一个字符串：描述操作结果的消息或错误消息。
- **主要流程**：
  1. 调用 `check_token` 验证 `user_id` 和 `token`。
  2. 若验证失败，返回错误状态码和消息。
  3. 若验证成功，生成一个新的 `terminal` 标识和临时 `token`，更新 `user` 集合中该用户的 `token` 和 `terminal` 字段。
  4. 如果更新失败，返回授权失败的状态码和消息。
  5. 若操作成功，返回状态码 `200` 和消息 `"ok"`。







## 拓展功能的实现

### 发货与收货

**发货**代码路径：`be/model/seller.py`

```python
    def send_books(self,user_id: str,order_id: str):

        res = self.db.new_order.find_one({"order_id": order_id})
        if res is None:
            return error.error_invalid_order_id(order_id)

        store_id = res["store_id"]
        books_status = res["books_status"]

        result = self.db.user_store.find_one({"store_id": store_id})
        seller_id = result["user_id"]

        if seller_id != user_id:
            return error.error_authorization_fail()

        if books_status == 0:
            return error.error_book_has_sent(order_id)

        if books_status == 2:
            return error.error_not_paid_book(order_id)

        if books_status == 3:
            return error.error_book_has_received(order_id)

        res = self.db.new_order.update_one({"order_id": order_id}, {"$set": {"books_status": 0}})
        assert res.modified_count > 0 #only for debug£¬it may also be equal to zero when multi-proc.
        return 200, "ok"
```

**参数**：

- `user_id`：用户的ID。
- `order_id`：订单ID。

**返回值**：

- 一个元组，包含以下两个元素：
  - 一个整数：表示状态码，`200` 表示操作成功，其他状态码表示错误。
  - 一个字符串：描述操作结果的消息或错误消息。

**主要流程**：

1. 从 `new_order`集合中查找与 `order_id` 匹配的订单。若未找到对应订单，返回状态码和无效订单ID错误消息。
2. 获取订单中的 `store_id` 和 `books_status`。从 `user_store` 集合中查找与 `store_id` 匹配的店铺信息，并获取该店铺的 `user_id`（卖家ID）。若卖家ID与 `user_id` 不一致，返回授权失败的状态码和错误消息。
3. 根据 `books_status` 值，检查订单的当前状态：
   - 若为 `0`，表示书籍已发货，返回相应错误消息。
   - 若为 `2`，表示书籍未付款，返回相应错误消息。
   - 若为 `3`，表示书籍已收货，返回相应错误消息。
4. 若订单状态允许发货，则更新 `books_status`为 0表示书籍已发货。若 `modified_count` 不大于 `0`，在调试模式下将触发断言（多进程情况下可能等于零）。
5. 若操作成功，返回状态码 `200` 和消息 `"ok"`。

**收货**代码路径：`be/model/buyer.py`

```python
    """
    - `user_id`：用户的ID。
	- `order_id`：订单ID。
	return: status_code,msg
    """
    def receive_book(self,user_id: str, order_id: str) -> (int, str):
        try :
            res = self.db.new_order.find_one({"order_id": order_id})
            if res == None:
                return error.error_invalid_order_id(order_id)
            buyer_id = res["user_id"]
            paid_status = res["books_status"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if paid_status == 1:
                return error.error_books_not_sent(order_id)#已经付钱，但是没有发货
            if paid_status == 2:
                return error.error_books_receive_without_payment(order_id)#没有付款就receive
            if paid_status == 3:
                return error.error_books_repeat_receive(order_id)
            self.db.new_order.update_one({"order_id": order_id}, {"$set": {"books_status": 3}})
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

```

**主要流程**：

1. 从 new_order集合中查找与 order_id 匹配的订单信息。如果订单不存在，返回状态码和无效订单ID错误消息。
2. 从查询结果中获取 buyer_id）和 books_status（订单状态）。如果 `buyer_id` 与传入的 `user_id` 不一致，返回授权失败的状态码和错误消息。
3. 检查 books_status的值以确定订单状态：
   - 若状态为 `1`，表示已付款但未发货，返回相应错误消息。
   - 若状态为 `2`，表示未付款便尝试收货，返回相应错误消息。
   - 若状态为 `3`，表示订单已确认收货，返回重复收货的错误消息。
4. 如果状态符合条件，更新 `books_status` 为 `3`，表示订单已确认收货。
5. 若操作成功，返回状态码 `200` 和消息 `"ok"`。
6. 若发生异常，捕获并返回状态码 `528` 和异常消息字符串

## 新增接口

**前端接口fe/access**：

这里主要是根据新增的路由添加对应的参数处理函数，将参数以post方式发送至对应的路由。这里值得一提的是，在debug过程中，若没有涉及比较复杂的数据准备，我们可以直接用postman工具来模拟访问某一路由。

**后端接口在 be/view/** ：

这里的修改与前端同理，主要是接受前端传递来的参数，然后根据其路由选择对应的函数进行处理。



## 新增的测试样例

**收获和发货测试代码**路径：`bookstore\fe\test\test_receive_and_delivery.py`。测试说明如下

**1. `test_send_ok`**

- **情况**：正常发货。
- **操作**：卖家发货。
- **预期结果**：发货成功，返回码为 `200`。

**2. `test_invalid_order_id_send`**

- **情况**：订单ID不存在的情况下尝试发货。
- **操作**：使用不存在的订单ID尝试发货。
- **预期结果**：发货失败，返回码不为 `200`。

**3. `test_authorization_error_send`**

- **情况**：使用不匹配的卖家ID尝试发货。
- **操作**：使用错误的卖家ID尝试发货。
- **预期结果**：发货失败，返回码不为 `200`。

**4. `test_books_repeat_send`**

- **情况**：重复发货。
- **操作**：卖家先进行一次发货，再次尝试发货。
- **预期结果**：第一次发货成功，返回码为 `200`；第二次发货失败，返回码不为 `200`。

**5. `test_receive_ok`**

- **情况**：正常接收。
- **操作**：买家付款后，卖家发货，买家接收。
- **预期结果**：接收成功，返回码为 `200`。

**6. `test_invalid_order_id_receive`**

- **情况**：订单ID不存在的情况下尝试接收。
- **操作**：使用不存在的订单ID尝试接收。
- **预期结果**：接收失败，返回码不为 `200`。

**7. `test_authorization_error_receive`**

- **情况**：使用不匹配的买家ID尝试接收。
- **操作**：使用错误的买家ID尝试接收。
- **预期结果**：接收失败，返回码不为 `200`。

**8.`test_books_not_send_receive`**

- **情况**：订单未发货情况下尝试接收。
- **操作**：买家付款后直接尝试接收，卖家未发货。
- **预期结果**：接收失败，返回码不为 `200`。

**9.`test_books_repeat_receive`**

- **情况**：重复接收。
- **操作**：买家在首次接收成功后再次尝试接收。
- **预期结果**：第一次接收成功，返回码为 `200`；第二次接收失败，返回码不为 `200`。





## 测试结果







## 遇到的问题







## 小组分工

lzj:





github协作图





