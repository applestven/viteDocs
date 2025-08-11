## @nestjs/sequelize

@nestjs/sequelize 是 NestJS 框架下对 Sequelize ORM 的封装插件，提供了基于装饰器的模型定义、依赖注入支持、事务管理、关联映射等功能，让 Sequelize 在 Nest 项目中更优雅地使用。

## ✅ 一句话理解

@nestjs/sequelize 就是 NestJS 框架对 Sequelize ORM 的“适配器”，让你能像使用 @InjectModel()、@Module() 那样结构化地组织数据库逻辑。

## 📦 安装

``` bash
npm install --save @nestjs/sequelize sequelize sequelize-typescript mysql2

```

##  🔧 使用方式（完整流程）

### 1️⃣ 模块初始化（AppModule 中引入）
``` typescript
import { SequelizeModule } from '@nestjs/sequelize';
import { User } from './models/user.model';

@Module({
  imports: [
    SequelizeModule.forRoot({
      dialect: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: '123456',
      database: 'demo',
      models: [User],
      autoLoadModels: true,
      synchronize: true, // 自动建表（生产环境建议 false）
      logging: false,
    }),
  ],
})
export class AppModule {}

```

## 2️⃣ 定义模型（使用装饰器定义数据库表结构）

``` typescript
import { Table, Column, Model, DataType } from 'sequelize-typescript';

@Table({ tableName: 'users' })
export class User extends Model {
  @Column({
    type: DataType.STRING,
    allowNull: false,
  })
  name: string;

  @Column(DataType.INTEGER)
  age: number;
}

```
## 3️⃣ 注册模型到模块

``` typescript
@Module({
  imports: [SequelizeModule.forFeature([User])],
  providers: [UserService],
  controllers: [UserController],
})
export class UserModule {}


```

## 4️⃣ 使用模型（通过依赖注入）

``` typescript
@Injectable()
export class UserService {
  constructor(
    @InjectModel(User)
    private userModel: typeof User,
  ) {}

  create(name: string, age: number) {
    return this.userModel.create({ name, age });
  }

  findAll() {
    return this.userModel.findAll();
  }
}


```

## 🔍 和其他 Node ORM 对比

| ORM             | Nest 支持               | 风格                       | 定义方式         | 生态适配       |
| --------------- | --------------------- | ------------------------ | ------------ | ---------- |
| **Sequelize**   | ✅ `@nestjs/sequelize` | 数据模型与逻辑分离（Active Record） | 类 + 装饰器      | 成熟，功能强大    |
| **TypeORM**     | ✅ `@nestjs/typeorm`   | 类似 Hibernate 的 Entity 映射 | 类 + 装饰器      | 官方推荐，文档丰富  |
| Prisma          | ✅ 手动集成                | Schema 文件生成              | 自动生成类型       | 静态类型好、轻量现代 |
| Objection.js    | ❌（手动接）                | SQL 风格清晰，基于 knex         | 手动写类 + query | 强类型，学习曲线高  |
| Mongoose（Mongo） | ✅ `@nestjs/mongoose`  | 文档数据库模型                  | Schema + 类   | Mongo 专用   |

## 🧩 支持的高级功能

🔁 一对多、多对多关联（@HasMany, @BelongsToMany）

✅ 自动同步数据库结构（开发环境用）

🔒 事务支持（sequelize.transaction() 或 Nest 注入方式）

🧪 测试友好（依赖注入 + mock 容易）

🧰 scopes, hooks, indexes 等 Sequelize 特性都可用

## 🧠 示例：一对多关联

```` typescript
@Table
export class User extends Model {
  @HasMany(() => Post)
  posts: Post[];
}

@Table
export class Post extends Model {
  @ForeignKey(() => User)
  @Column
  userId: number;

  @BelongsTo(() => User)
  user: User;
}
```