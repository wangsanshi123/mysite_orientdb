该项目是ngpyorient和ngrestframwork的具体使用的简单demo。
注：1 ngpyorient（源码见该项目的ngpyorient模块）是基于pyorient的编写的OGM，
    在编写的过程中尽量和Django的ORM保持一致。基本用法实例：
    a.创建：Person.objects.create(name="yuan1")
    b.查询:Person.objects.filter(name__startswith="yuan", age__gte=1)
    c.更新：Person.objects.filter(age__gte=0).update(age=2)
    d.删除：Person.objects.filter(name="zhang2", age=1).delete()
    e.跨节点查询（通过关系likes）:Person.objects.filter(Out("likes"), Out("produced"))
    详细用法可以参考测试用例tests_ogm/ogm_test

   2 OGM(Object Graph Mapping)类似于ORM(Object Relational Mapping)，区别是OGM用于图数据库(Graph)的，
   而ORM用于关系型数据库



