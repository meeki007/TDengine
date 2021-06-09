###################################################################
#           Copyright (c) 2016 by TAOS Technologies, Inc.
#                     All rights reserved.
#
#  This file is proprietary and confidential to TAOS Technologies.
#  No part of this file may be reproduced, stored, transmitted,
#  disclosed or used in any form or by any means other than as
#  expressly provided by the written permission from Jianhui Tao
#
###################################################################

# -*- coding: utf-8 -*-

import sys
import taos
from util.log import tdLog
from util.cases import tdCases
from util.sql import tdSql
from util.dnodes import tdDnodes
import random

class TDTestCase:
    def init(self, conn, logSql):
        tdLog.debug("start to execute %s" % __file__)
        tdSql.init(conn.cursor(), logSql)

        self.ts1 = 1593548685000    
        self.ts2 = 1593548785000    


    def run(self):
        # tdSql.execute("drop database db ")
        tdSql.prepare()
        tdSql.execute("create table st (ts timestamp, num int,  value int , t_instance int) tags (loc nchar(30))")
        node = 5
        number = 10
        for n in range(node):
            for m in range(number):
                dt= m*300000+n*60000  # collecting'frequency is 10s 
                args1=(n,n,self.ts1+dt,n,100+2*m+2*n,10+m+n)
                # args2=(n,self.ts2+dt,n,120+n,15+n)
                tdSql.execute("insert into t%d using st tags('beijing%d')  values(%d, %d, %d, %d)" % args1)
                # tdSql.execute("insert into t1 using st tags('shanghai') values(%d, %d, %d, %d)" % args2)             
                
        # interval function
        tdSql.query("select avg(value) from st interval(10m)")
        print(tdSql.queryResult)
        tdSql.checkRows(6)        
        tdSql.checkData(0, 0, "2020-07-01 04:20:00")
        tdSql.checkData(1, 1, 107.4)
       
        # subquery with interval
        tdSql.query("select avg(avg_val) from(select avg(value) as avg_val from st where loc='beijing0' interval(10m));")
        tdSql.checkData(0, 0, 109.0)

        # subquery with interval and select two Column in parent query
        # tdSql.query("select ts,avg(avg_val) from(select avg(value) as avg_val from st where loc='beijing0' interval(10m));")

        # subquery with interval and sliding 
        tdSql.query("select avg(value) as avg_val from st where loc='beijing0' interval(8m) sliding(30s) limit 1;")   
        tdSql.checkData(0, 0, "2020-07-01 04:17:00")
        tdSql.checkData(0, 1, 107.4) 
        tdSql.query("select avg(avg_val) from(select avg(value) as avg_val from st where loc='beijing1' interval(8m) sliding(30s));")
        tdSql.checkData(0, 0, 111)
        
        # subquery with interval and offset
        tdSql.query("select avg(value) as avg_val from st where loc='beijing0' interval(5m,1m);")
        tdSql.checkData(0, 0, "2020-07-01 04:21:00")
        tdSql.query("select avg(avg_val) from(select avg(value) as avg_val from st where loc='beijing0' interval(5m,1m));")
        tdSql.checkData(0, 0, 111)

        # subquery  with interval,sliding and group by ; parent query with interval
        tdSql.query("select avg(value) as avg_val from st where loc='beijing0' interval(8m) sliding(1m) group by loc limit 1 offset 52 ;")
        tdSql.checkData(0, 0, "2020-07-01 05:09:00")
        tdSql.checkData(0, 1, 118)
        tdSql.query("select avg(avg_val) from(select avg(value) as avg_val from st where loc!='beijing0' interval(8m) sliding(1m)  group by loc )interval(5m);")
        tdSql.checkData(0, 0, 111)

        # #  subquery and parent query with interval and sliding 
        # tdSql.query("select avg(avg_val) from(select avg(value) as avg_val from st where loc='beijing1' interval(8m) sliding(30s)) interval(5m) sliding(1s);")
        # tdSql.checkData(0, 0, 111)

        # subquery and parent query with top and bottom
        tdSql.query("select top(avg_val,2) from(select avg(value) as avg_val,num from st where loc!='beijing0' group by num);")
        tdSql.checkData(0, 0, 111)
        tdSql.query("select bottom(avg_val,2) from(select avg(value) as avg_val,num from st where loc!='beijing0' group by num);")
        tdSql.checkData(0, 0, 111)





        # tdSql.query("select avg(voltage) from st interval(1n, 15d)")

        # tdSql.query("select avg(voltage) from st interval(1n, 15d) group by loc")

        # tdDnodes.stop(1)
        # tdDnodes.start(1)
        # tdSql.query("select last(*) from t interval(1s)")
        

        # tdSql.query("select first(ts),twa(c) from tb interval(14a)")
        # tdSql.checkRows(6)

        # tdSql.query("select twa(c) from tb group by c")
        # tdSql.checkRows(4)


    def stop(self):
        tdSql.close()
        tdLog.success("%s successfully executed" % __file__)


tdCases.addWindows(__file__, TDTestCase())
tdCases.addLinux(__file__, TDTestCase())
