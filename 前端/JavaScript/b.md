## GC
    参考地址：https://blog.csdn.net/qq_42543177/article/details/124644363

## 什么是程序中的垃圾
 当一个变量没有被其他变量或属性引用的时候 ， 这个变量就是程序的的垃圾 。 其所占用的内存就需要被释放  
## 变量中的生命周期 
全局作用域 
描述： 定义在所有函数之外的变量
生命周期 ：会持续到浏览器关闭页面 
局部变量：
函数执行过后就结束了 ， 此时便可释放内存（垃圾回收）

## 数据存储（栈、堆） ：
 基本数据类型存储在“ 栈 ”中 ， 以及存储在 “ 堆 ”中的复杂类型 的引用也存储在“ 栈 ”中  

 当一个对象没有被引用 ，也就是在栈中无变量存储该对象引用地址 ，那么此对象占的内存就会被释放

## 垃圾回收的两种方法 
理解 ： 垃圾回收器会周期性的释放程序中已经不在被引用的垃圾对象。那如何判断哪些被引用了，哪些不再被引用？通常会使用以下两种方法来进行判断 

1.   标记清除法 
标记 ： 从根节点遍历 ，对可访问的对象进行标记
清除 ：在没有可分快的时候 ， 对堆内存遍历 ，将没有被标记的对象清除 
优缺点 ： 实现简单 ； 内存过于碎片化 ，内存分配速度慢
解决办法： 标记-整理法 ： 主要不同的是将被引用的对象移动到一段，然后清理掉标记的内存

2.   引用计数法 
引用计数法就是追踪每个变量被引用的次数，当引用数为0将可以被回收掉。
优点：当引用数为0时会被立即回收
缺点：a 计数器的增减处理频繁，会导致空间的使用效率降低。
   b 循环引用无法收回，导致内存泄漏。
  若有一函数Person中a引用了b，b引用了a。每次调用函数Person，它们的引用计数都不为0，则永远不能被回收。

## 分代式垃圾回收机制 
V8引擎 将内存分为 新生代 和 老生代  新生代对象存活时间较短 ，内存通常在1-8mb ，老生代存储存活时间较长和常驻内存的对象。对于两个区域的回收频率不同 ，所以V8采用了两个垃圾回收器来管控 

一 、 新生代垃圾回收 
新生代采用Scavenge策略进行垃圾回收 ，在具体实现中 ， 主要采用了复制式的方法cheney算法 ，
Cheney算法将新生代也分为两个区 ， 使用区 和 空闲区  作用就如其名 。 新加入的对象会被存放到使用区 ， 当使用区快被写满时 ，就执行一次垃圾回收操作 
- 标记活动的对象 
- 将标记的对象复制到空闲区并进行排序  
- 将原先的使用区内存进行释放 
- 最后角色互换  ， 使用区变成了空闲区 

二 、 新生代 对象 何时到老生代 
第一种情况 ， 经过多次复制后被认为是活动性较强的对象 会被移到老生区代管 
第二种情况 ， 当一个对象复制到空闲区 ，内存占用超过25% ， 直接移到老生代 原因当Scavenge回收后 ，空闲区转变为使用区，需进行内存分配 ，若占比过大，会影响后期的内存分配 

##  并行回收 
javaScript 是一门单线程的语言 ， 当我们进行gc垃圾回收时 ， 会阻塞js脚本的运行， 需要等待垃圾回收完成 在恢复脚本的运行 ， 这种情况叫 “ 全停顿 ” ，当GC时间过长  ，就会造成页面卡顿 。解决办法就是引入辅助线程来进行同时处理 ，V8引入了并行回收机制 
新生代空间就采用并行策略 ，启动多个线程对新生代的垃圾清理 ,这些线程同时将对象空间的数据移入空闲区 。 由于这个过程会发生内存地址的改变，所以还需要同步更新引用这些对象的指针 。

## 老生代垃圾回收 

老生代因为大多是存活的对象，不需要时常清除更新 ，采用“标记整理”法释放内存

1. 增量标记  
并行策略虽然可以增加垃圾回收的效率 ， 对于新生代这种存放较小对象的回收器能有很好的优化 ，但其实还是全停顿式的 。所以对于老生代来说 ，哪怕使用并行策略还是会消耗大量时间。 于是就有了：
“ 增量标记 ” ：将一次GC 分为多步小GC ， 让js和小GC 交替执行 ，直到标记完成  。 

而后又是如何进行下一次小GC 标记？如果执行JS任务时刚被标记好的对象引用又被修改了该当如何？V8解决这两个问题的方法分别是三色标记法和写屏障。

解决问题一：三色标记法

标记清理法区分是通过非黑即白的策略，
所以采用了三色标记法，使用每个对象的两个标记位和一个标记工作表来实现标记，两个标记位编码三种颜色：黑（11），白（00），灰（10）。

黑色表示对象自身及对象的引用都被标记（已检查状态）
白色表示未被标记的对象（初始状态）
灰色表示自身被标记，自身的引用未被标记（待检查状态）

初始将所有对象都是白色
从root对象开始，先将root对象标记为灰色并推入标记工作表中
当收集器从标记工作表中弹出对象并访问他的所有引用对象时，自身灰色就会变成黑色。
将自身的下一个引用对象标记为灰色
一直这样执行下去，直到没有可以被标记为灰色的对象时，剩下的白色对象都是不可达的，进入清理阶段。恢复时从灰色标记对象开始执行。





## 懒性清理
增量标记完后，如果当前内存足以支持代码的快速运行，也没必要立即清理，可让程序先运行，也无需一次性清理完所有垃圾对象，可以按需清理直到所有垃圾对象清理完后再继续增量标记。



## 并发回收
并发主要发生在工作线程上。当在工作线程（辅助线程）执行GC是，应用程序可以继续在主线程运行并不会被挂起。
这也是有问题的，因为GC也在进行，应用程序也在执行，此时对象的引用关系随时都有可能变化，所以之前做的一些标记就需要改变，所以需要读写锁机制来控制这一点。