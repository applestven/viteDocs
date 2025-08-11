
## class-validator
class-validator 是一个用于 TypeScript 和 JavaScript 的对象验证库，通常搭配 class-transformer 一起使用，尤其在 NestJS、Express 等框架中用于 数据校验（DTO 校验）。其核心思想是基于类和装饰器（Decorator）来声明字段的验证规则。

总结：class-validator 让你可以在类的属性上使用装饰器，如 @IsString()、@IsInt() 来声明验证规则，自动校验前端传入的数据是否符合预期。

``` bash
npm install class-validator class-transformer
```


## ✅ 使用前 vs 使用后对比
## 🚫 使用前（手动校验）

``` js
function validateUserInput(input: any) {
  if (typeof input.name !== 'string') {
    throw new Error('name must be a string');
  }
  if (typeof input.age !== 'number') {
    throw new Error('age must be a number');
  }
}

```

手动写逻辑，容易出错，代码重复度高，维护困难。

## ✅ 使用后（使用 class-validator）

``` ts
import { IsString, IsInt, MinLength, Min } from 'class-validator';

class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string;

  @IsInt()
  @Min(0)
  age: number;
}

```

## 🛠 在 NestJS 中的应用（自动集成）

``` ts
// main.ts
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(new ValidationPipe());  // 启用全局验证
  await app.listen(3000);
}
```

``` ts
// user.dto.ts
export class CreateUserDto {
  @IsString()
  name: string;

  @IsInt()
  age: number;
}

```

``` ts
// controller.ts
@Post()
create(@Body() createUserDto: CreateUserDto) {
  // 如果传入数据不符合 DTO 定义，会自动抛出 400 错误
}

```



## 总结 

| 对比项   | 手动校验    | `class-validator`  |
| ----- | ------- | ------------------ |
| 代码可读性 | 差，逻辑混乱  | 高，结构清晰             |
| 可复用性  | 低，重复逻辑多 | 高，可定义通用 DTO        |
| 类型安全  | 不易维护    | TS 类型推导配合装饰器，强类型   |
| 适配框架  | 无自动支持   | 与 NestJS 等主流框架高度集成 |



## 📌 常见装饰器示例
| 装饰器             | 含义         |
| --------------- | ---------- |
| `@IsString()`   | 必须是字符串     |
| `@IsInt()`      | 必须是整数      |
| `@IsBoolean()`  | 必须是布尔值     |
| `@IsEmail()`    | 必须是邮箱格式    |
| `@IsOptional()` | 该字段是可选的    |
| `@Min(x)`       | 数值不能小于 x   |
| `@MaxLength(n)` | 字符串最大长度为 n |
| `@IsIn([...])`  | 值必须在给定列表中  |

##  swagger
@ApiProperty() 是专门给 Swagger 文档看的，它不会影响实际逻辑，只是为了自动生成接口文档中每个字段的说明、类型、示例、是否必填等信息。

