数据库地址：
http://10.60.49.214:2480/studio/index.html#/database/test1/browse

localhost:8000
localhost:8000/persons
localhost:8000/persons/?name=yuan1
localhost:8000/persons/?to=b_friend__o_eat"&name="zhang"


数据库的连接没有维护

orientdb 问题：

1 同一个connect,只会查询到建立连接那一刻之前的数据，连接建立后，其connection插入的数据，当前connection查不到
2 即使是当前connection插入的数据，当前connection也查看不到

3 graph和Node及RelationShip的绑定必须在class的声明之后


已实现：
list
pagination

待实现：
retrive
create
upate
destroy

permissions
filter
search


OGM实现：
1 查询
Person.objects.all()

Person.objects.filter(name='zhang')
Person.objects.get(name='zhang')
Entry.objects.all().filter(pub_date__year=2006)
Entry.objects.all()[5:10]
Entry.objects.order_by('headline')[0:1].get()
2 增加
Person.objects.create(name="Ringo Starr")


Person(name="Fred Flintstone", shirt_size="L")
p.save()


3 删除：
Entry.objects.filter(pub_date__year=2005).delete()

4 更新：
Entry.objects.filter(pub_date__year=2005).update(name="zhang")

实现

Person.objects.all()


OGM架构图：
Person.objects.all()-------------------------------->SQLCompiler(QueryBuilder(manager))--result


Person.objects.filter()--->QuerySet(sql，manager)--->all()--->SQLCompiler(QueryBuilder(manager))--result

querySet(sql，manager).filter()--->QuerySet(sql，manager)



todo:

1 或查询(Q查询)
select from person where name="yuan1" or name="yuan2" and age>=1
select from person where name="yuan2" and age>=1 or  name="yuan1"



2  sql语句

3 select in() from Person where province.name="湖北"

  #person----lives---->country
  #person----owns ---->car
  #shows the countries where there are users that own a Ferrari.
  SELECT name FROM ( SELECT EXPAND( IN('Owns').OUT('Lives') )FROM Car WHERE name LIKE '%Ferrari%' )


select out() from province
select expand(out()) from province
select out() from province where name="hubei"
select expand(out()) from province where name="hubei"





1 或查询(Q查询)
select from person where name="yuan1" or name="yuan2" and age>=1
select from person where name="yuan2" and age>=1 or  name="yuan1"


2 更新
update Person set name='zha1' WHERE name = 'yuan1'
update Person set name='zha1' WHERE @rid = #79:0
update Person  CONTENT {'name': 'yu', 'age': 3} WHERE @rid = #79:0

todo

rest-framework
serialize 的allow_null ,allow_blank ,required
1 update

2 relationship的创建，删除（与restful结合）

3 删除relation前：判断其起点的实例必须和其终点的一个实例有关联

select edge Likes WHERE @rid = '#194:0
select from [#194:0]

子查询
1 select from let $edge = select from [#196:0]
2
select name from Person
let $tmp = (select name from Person where name ='yuan1')
where name = first($tmp).name

3 通过关系查找节点
select expand(out) from likes where out.name="yuan3"
select expand(in) from likes
select expand(in,out) from likes

select expand(out) from likes where out.name="yuan2" and in.@class="phone"
select expand(out) from borned where out.name="yuan2" and in.@class="province"




应该等价于下面的语句：
select expand(in()) from phone      #支持
select expand(in()) from phone where in.name="yuan2"  #不支持

traverse in() from phone
select from (traverse in() from phone) where @class="person" and name="yuan3" #支持（等价）

4 unionall
select expand($c)
let $a = (select from person where name="yuan1"),
$b = (select from person where name="yuan2"),
$c = unionAll($a,$b)

select expand($c)
let $a = (select from province),
$b = (select from person where name="yuan2"),
$c = unionAll($a,$b)


select expand($c)
let $a = (select expand(out) from borned where out.name="yuan2" and in.@class="province"),
$b = (select expand(in) from borned where out.name="yuan2" and in.@class="province"),
$c = unionAll($a,$b)

================================================

4.1 intersect
select expand($c)
let $a = (select expand(out) from borned where out.name="yuan2" and in.@class="province"),
$b = (select expand(in) from borned where out.name="yuan2" and in.@class="province"),
$c = intersect($a,$b)


let $project = select from [#196:0]
let $counter = select from first($project).out
return first($counter).@class

##let $project = select from [#196:0]
##return $project
##
##select $all from person
##let $all = ( traverse out('likes') from $parent.$current)
##
##traverse out('likes') from person
##
##select expand(in('likes')) from person
##select in('likes') from person
5 创建关系
create edge likes from

6 删除关系
select from person where out[@class="car"].name='aodi'

select from person where out.@class="car"

delete vertex person where out[@class= "car"].name='aodi'

DELETE VERTEX person WHERE in[@Class = 'HasAttachment'].date

DELETE VERTEX from （select from [#88:0, #89:0]）

select from [#87:0, #88:0]



7 更新关系
UPDATE EDGE Friend SET out = (SELECT FROM Person WHERE name = 'John') WHERE foo = 'bar'
UPDATE EDGE Likes SET in = #203:0 where in = #202:0
UPDATE EDGE Likes SET in = (select from car where name='dazhong') where in = #203:0

UPDATE EDGE Likes SET in = #203:0 and out = #107:0 where in = #202:0

update edge Likes set in=#172:0,md5="123" WHERE in = #172:0 and out =#106:0
update edge Likes set in=#171:0,out=#105:0 WHERE in = #172:0 and out =#106:0
update edge Likes set in=#171:0,out=#105:0,md5='123' WHERE in = #172:0 and out =#106:0







