通过关系查询(select,traverse)

#person----lives---->province
#person----likes ---->car
#person----likes ---->phone
#car ----produced --->province

#person----lives---->province
    |                  |
    |                produced
    |                  |
    |---------likes ---->car
    |---------likes ---->phone


查找：select
1 Get all the outgoing edges from all the vertices:
SELECT outE() FROM V
SELECT outE() FROM Person

SELECT expand(outE("borned")) FROM person  where name="yuan2"

SELECT FROM (
    SELECT EXPAND(BOTHE('liked')) FROM Tag WHERE prop='name'
) WHERE in.prop='brand' or out.prop='brand'

SELECT FROM (
    SELECT EXPAND(BOTHE('liked')) FROM Person
) WHERE in.brand='brand' or out.brand='brand'


SELECT EXPAND(BOTHE('likes')) FROM phone
SELECT EXPAND(inE('likes')) FROM phone
SELECT EXPAND(in('likes')) FROM phone

SELECT EXPAND(out('likes')) FROM person
SELECT EXPAND(outE('likes')) FROM person

#对起点过滤
 EXPAND(out('likes')) FROM person where name="yuan1"

#对起点，终点同时过滤
select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where name="dazhong"
select from (SELECT EXPAND(out('likes').in('have')) FROM person where name="yuan1")
select from (SELECT EXPAND(out('likes').in('have')) FROM person where name="yuan1")  where name ='USA'


select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where @class='car'
select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where (@class='car' and name='dazhong') or(@class='phone')

select from (SELECT EXPAND(in('likes')) FROM car ) where (@class='person' and name="yuan1")
select from (SELECT EXPAND(in('likes')) FROM car ) where (@class='person' and name="yuan1") and (@class='person' and age=1)


select from (select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where (@class='car' and name='dazhong') or(@class='phone')) where name='dazhong'



###
select from (select EXPAND(out('likes')) from Person  WHERE name = 'yuan1')  WHERE ((name = 'aodi' and @class = 'car') OR (brand = 'xiaomi' and @class = 'phone'))
select from (select EXPAND(out('likes').in('have')) from Person  WHERE name = 'yuan1')  WHERE ((name = 'aodi' and @class = 'car') OR (brand = 'xiaomi' and @class = 'phone'))
2 traverse

TRAVERSE out() FROM person
#对终点过滤
SELECT FROM (TRAVERSE out() FROM person) where @class='car'
SELECT FROM (TRAVERSE out() FROM person) where @class='car' and name='dazhong'

#对起点，终点同时过滤
SELECT FROM (TRAVERSE out() FROM (select from person where name='yuan1')) where @class='car' and name='dazhong'
SELECT FROM (TRAVERSE out() FROM (select from person where name='yuan1')) where (@class='car' and name='dazhong') or(@class='phone')



3 unionall
SELECT EXPAND( $c ) LET $a = ( SELECT FROM E ), $b = ( SELECT FROM V ), $c = UNIONALL( $a, $b )

SELECT EXPAND( $c ) LET $a = ( SELECT FROM person ), $b = ( SELECT FROM car ), $c = UNIONALL( $a, $b )
SELECT EXPAND( $c ) LET $a = ( select expand(in) from likes ), $b = ( select expand(out) from likes  ), $c = UNIONALL( $a, $b )


4 通过关系过滤定点
select expand(out) from likes where out.name="yuan2" and in.@class='car'
select expand(in) from likes where out.name="yuan2" and in.@class='car'
let $a = select  from likes where out.name="yuan2" and in.@class='car'



todo
filter
{""}


http://127.0.0.1:8000/persons/?name=yuan3
http://127.0.0.1:8000/persons/?name=yuan3,yuan4

http://127.0.0.1:8000/persons/?search=yua
http://127.0.0.1:8000/persons/?search=yua zhang

5 多表关联

SELECT   FROM (TRAVERSE both() FROM (select from person))
SELECT   FROM (TRAVERSE both() FROM (select from person)  MAXDEPTH  1)
SELECT EXPAND(both()) FROM person

6 LinkSet
CREATE LINK comments TYPE LINKSET FROM comments.PostId TO posts.Id INVERSE

CREATE LINK departments TYPE LINKSET FROM Department.id To person.department_id INVERSE

select from person

7 通过关系查询
select name,oute()[0],ine() from person
select name,oute()[0] as e,ine() from person where e.out.@class="car"
select name,oute()[0].out as e,ine() from person

select name,oute().out.name as e,ine() from person

select name,oute().in.name as e,ine() from person

select name,bothe().in.name,ine() from person
select name,bothe().in.name as name_,bothe().in.brand as brand,ine() from person
select bothe().in.name as name,bothe().in.brand as brand from person
select bothe("likes").in.name as name,bothe("likes").in.brand as brand from person


select name,bothe().in.name as name_,bothe().in.brand as brand,ine() from person where bothe().in.brand contains "huawei"
select name,bothe().in.brand as phone_brand,ine() from person where bothe().in.@class="phone"



select name,bothe().in.name,ine() from person where bothe().in.@class='car'
select name,bothe().in.name,ine() from person where bothe().in.@class='car'


select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price,bothe("likes").in.brand as brand from person
select name,unionall(car_name,car_price),bothe("likes").in.name as car_name,bothe("likes").in.price as car_price,bothe("likes").in.brand as brand from person

select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price,bothe("likes").in.brand as brand ,unionall(bothe("likes").in.name ,bothe("likes").in.price) from person
select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price,bothe("likes").in.brand as brand ,unionall(bothe("likes").in.name ,bothe("likes").in.brand ) from person
select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price from person
select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price,unionall(bothe("likes").in.name,bothe("likes").in.price)from person


select in() from person
select expand(out()) from person where out().@class="car"
select expand(out()) from person where oute.="bored"
select expand(out()) from person where out().@class="car" or oute().@class='borned'
select expand(out("bornd")) from person


select name,bothe().in.name,ine() from person where (bothe().in.@class='car' and bothe().in.name="aodi") or (bothe().@class='borned' and bothe().in.name="hubei")
select name,both("borned"),both("likes")from person

select name,both("borned").name as borned,both("likes").name as likes ,both("borned").@class as class from person


select name,both("borned").name as province__name,both("likes").name as car__name ,both("likes").price as car__price,both().@class as class from person

select  from (select name,both("borned").name as province__name,both("likes").name as car__name ,both("likes").price as car__price,both().@class as class from person) where car__name contains "aodi"
select  from (select name,both("borned").name as province__name,both("likes").name as car__name ,both("likes").price as car__price,both().@class as class from person) where both("likes").name contains "aodi"

select expand(both("borned").name) from person
select expand(both("likes").name) from person

select from (select expand(both("borned").name) from person,select expand(both("likes").name) from person)


8 修改节点的关系
UPDATE ServerRecord SET in_ServerBasicToServerRecord__new=["#2484:100"]  WHERE @rid=#160:0

UPDATE Persons SET phone=000000, out_Inside=(
  select from Rooms where room_id=5) where person_id=8

UPDATE serverrecord SET in_ServerRecordToIDC=(
  select * from `idc` where @rid=#811:0) where @rid=#160:0

9
select outE(likes) from person



#todo

SELECT EXPAND(out('likes')) FROM person where name="yuan1"
select EXPAND(out('ServerBasicToServerRecord__new')) from ServerRecord  WHERE @rid = '#160:0'


select EXPAND(out('ServerBasicToServerRecord__new')) from ServerRecord

SELECT EXPAND(out('likes')) FROM person