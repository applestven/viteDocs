## @nestjs/swagger

@nestjs/swagger 是 NestJS 官方提供的插件，用于 自动生成基于 Swagger（OpenAPI 规范）的接口文档，开发者只需用装饰器标注 DTO 和接口方法，即可生成交互式 API 文档页面，省去手写文档的烦恼。

### 安装

```bash
npm install --save @nestjs/swagger swagger-ui-express
```

### 配置    

```typescript
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const options = new DocumentBuilder()
    .setTitle('API 文档')
    .setDescription('API 文档描述')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, options);
  SwaggerModule.setup('api-docs', app, document);
  await app.listen(3000);
}
bootstrap();
```

### 装饰器

#### @ApiTags

用于给控制器添加标签，方便在文档中分类展示。

```typescript
@ApiTags('用户')
@Controller('users')
export class UsersController {}
```

#### @ApiOperation

用于给接口方法添加描述。

```typescript
@ApiOperation({ summary: '获取用户列表' })
@Get()
findAll() {
  return 'This action returns all users';
}
```

#### @ApiParam

用于给接口方法中的参数添加描述。

```typescript
@ApiParam({ name: 'id', required: true, description: '用户 ID' })
@Get(':id')
findOne(@Param('id') id: string) {
  return `This action returns a #${id} user`;
}
```

#### @ApiQuery

用于给接口方法中的查询参数添加描述。

```typescript
@ApiQuery({ name: 'name', required: false, description: '用户名' })// ...
```

#### @ApiBody

用于给接口方法中的请求体添加描述。

```typescript
@ApiBody({
  type: CreateUserDto,
  description: '创建用户请求体',
  examples: {
    a: {
      summary: '示例1',
      value: {
        name: '张三',
        age: 18,
      },
    },
    b: {
      summary: '示例2',
}
```

##  📌 常见装饰器示例
| 装饰器                          | 功能                                 |
| ---------------------------- | ---------------------------------- |
| `@ApiProperty()`             | DTO 字段说明                           |
| `@ApiTags()`                 | 控制器分组名                             |
| `@ApiOperation({ summary })` | 接口方法的说明                            |
| `@ApiResponse({ ... })`      | 指定响应结构                             |
| `@ApiQuery()`                | 声明查询参数                             |
| `@ApiParam()`                | 声明路径参数                             |
| `@ApiBody()`                 | 自定义请求体结构（通常用不到）                    |
| `@ApiBearerAuth()`           | 声明使用 JWT 认证（配合 `.addBearerAuth()`） |


## 参考

| 功能       | 使用方式                                    |
| -------- | --------------------------------------- |
| 文档入口设置   | `SwaggerModule.setup()`                 |
| DTO 字段说明 | `@ApiProperty()`                        |
| 控制器分组    | `@ApiTags()`                            |
| 接口摘要说明   | `@ApiOperation()`                       |
| 请求参数说明   | `@ApiQuery()` / `@ApiParam()`           |
| 返回结构说明   | `@ApiResponse()`                        |
| 支持 JWT   | `@ApiBearerAuth()` + `.addBearerAuth()` |
