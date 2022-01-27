# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 13:33:05 2018

@author: sunil.dabbiru
"""

# myscript.py

#from __future__ import print_function
from mattermostdriver import Driver
#import pycurl
#import certifi
import requests
#from StringIO import StringIO
#import os
import cx_Oracle
#import pandas as pd
#import matplotlib.pyplot as plt
#from matplotlib import style
#buffer = StringIO()
#c = pycurl.Curl()
#c.setopt(c.URL,'https://www.website.info/mattermost/hooks/XXXXXXX')

#data = {"text": "This is TestX"}
#response = requests.post('https://www.website.info/mattermost/hooks/XXXXXXX', json=data)
#print(response.status_code)


foo = Driver({
     'scheme': 'https',   
     'url': 'www.website.info',
     'token': 'XXXXXXXXXXXX',
     'port': 443,
     'debug': False,
     #'verify' : False
    
})

foo.login()
webhook_url = 'https://www.website.info/mattermost/hooks/XXXXXXXX'

claims_sql = """
SELECT "WEEK","INITIAL",NVL2(INIT_PCT,INIT_PCT||'%',NULL) "INIT_PCT","REOPENED",NVL2(REOP_PCT,REOP_PCT||'%',NULL)  "REOP_PCT","CONTINUED",NVL2(CONT_PCT,CONT_PCT||'%',NULL) "CONT_PCT"
FROM
(
SELECT 
         WK||': '||TO_CHAR(WK_BEGIN_DT, '{MM/DD - ') || TO_CHAR(WK_BEGIN_DT + 6, 'MM/DD')||'}' "WEEK",
         TO_CHAR(INIT_CNT,'999,999') "INITIAL",
         ROUND(((INIT_CNT-LAG(INIT_CNT) OVER (ORDER  BY WK_BEGIN_DT))/LAG(INIT_CNT) OVER (ORDER  BY WK_BEGIN_DT))*100,2)
         "INIT_PCT",
         TO_CHAR(REOP_CNT,'999,999') "REOPENED",
         ROUND(((REOP_CNT-LAG(REOP_CNT) OVER (ORDER  BY WK_BEGIN_DT))/LAG(REOP_CNT) OVER (ORDER  BY WK_BEGIN_DT))*100,2)
         "REOP_PCT",
         TO_CHAR(CONT_CNT,'999,999') "CONTINUED",
         ROUND(((CONT_CNT-LAG(CONT_CNT) OVER (ORDER  BY WK_BEGIN_DT))/LAG(CONT_CNT) OVER (ORDER  BY WK_BEGIN_DT))*100,2)
         "CONT_PCT"
    FROM (
            SELECT TRUNC (CREATE_DT, 'DAY') WK_BEGIN_DT,
                   ROUND(TO_NUMBER(TO_CHAR(NEXT_DAY(TRUNC(CREATE_DT),'SUN'),'ddd'))/7) WK,
                   SUM(CASE RECORD_SUB_TYPE_CD WHEN 'INCM' THEN 1 ELSE 0 END) INIT_CNT,
                   SUM(CASE RECORD_SUB_TYPE_CD WHEN 'ROCM' THEN 1 ELSE 0 END) REOP_CNT,
                   SUM(CASE RECORD_SUB_TYPE_CD WHEN 'WCRT' THEN 1 ELSE 0 END) CONT_CNT
              FROM UI_RECORD_SEARCH_V A
             WHERE TRUNC (CREATE_DT) >= '1 MAR 2020'
                   AND A.RECORD_SUB_TYPE_CD IN ('ROCM', 'INCM', 'WCRT')
          GROUP BY TRUNC (CREATE_DT, 'DAY'),ROUND(TO_NUMBER(TO_CHAR(NEXT_DAY(TRUNC(CREATE_DT),'SUN'),'ddd'))/7)
    )
    )
ORDER BY 1 DESC
"""

ssa_sql = """
  SELECT TO_CHAR(sub.create_dt) AS "DATE",
         TO_CHAR((sub.SSA_AUTH_N + sub.SSA_AUTH_Y),'999,999') NEW_CLMT_CNT,
         TO_CHAR(sub.SSA_AUTH_Y,'999,999') "SSA_AUTH_Y",
         TO_CHAR(sub.SSA_AUTH_N,'999,999') "SSA_AUTH_N",
         TO_CHAR(ROUND (sub.SSA_AUTH_N / (sub.SSA_AUTH_N + sub.SSA_AUTH_Y) * 100, 2))||'%'
            SSA_AUTH_N_PCT,
         TO_CHAR(sub.SSA_DOWN_PEND_ISS,'999,999') "SSA_DOWN_PEND_ISS",
         TO_CHAR(ROUND (
            sub.SSA_DOWN_PEND_ISS / (sub.SSA_AUTH_N + sub.SSA_AUTH_Y) * 100,
            2))||'%'
            SSA_DOWN_PEND_PCT
    FROM (  SELECT TRUNC (c.CREATE_DT) CREATE_DT,
                   SUM (CASE WHEN c.SSA_AUTH_IN = 'Y' THEN 1 ELSE 0 END)
                      SSA_AUTH_Y,
                   SUM (CASE WHEN c.SSA_AUTH_IN = 'Y' THEN 0 ELSE 1 END)
                      SSA_AUTH_N,
                   SUM (CASE WHEN i.ISSUE_ID IS NOT NULL THEN 1 ELSE 0 END)
                      SSA_DOWN_PEND_ISS
              FROM ui_claimant_v c
                   JOIN ui_claim_v cl ON c.claimant_id = cl.claimant_id
                   LEFT JOIN ui_issue_v i
                      ON     i.CLAIMANT_ID = cl.CLAIMANT_ID
                         AND i.CLAIM_ID = cl.CLAIM_ID
                         AND i.SUB_TYPE_CD = 'ISOC'
                         AND i.status_cd = 'PEND'
             WHERE c.create_dt >= TO_DATE ('14-MAR-2020 21', 'DD-MM-YYYY HH24')
          GROUP BY TRUNC (c.CREATE_DT)) sub
ORDER BY sub.create_dt DESC
"""
fpuc_sql = """
SELECT  /*+parallel(8)*/  TO_CHAR(A.RQST_WK_DT) AS RQST_WK_DT,
TO_CHAR(COUNT(DISTINCT A.CLAIMANT_ID),'999,999') CLMT_RCVD_FPUC_CNT, 
TO_CHAR(SUM(NVL(A.AUTH_AM,0)),'$999,999,999.00')  TOT_AUTH_AM
FROM UI_AUTH_PMT_V A
WHERE A.RQST_WK_DT >= '29-MAR-2020' AND A.STATUS_CD = 'PROC'
AND A.SECTION30_IN = 'N'
AND A.FAC_AM = 600
GROUP BY RQST_WK_DT
ORDER BY A.RQST_WK_DT DESC
"""

peuc_sql = """
WITH PEUC_DATA AS  
(SELECT  * FROM UI_CLAIM_V CLM WHERE 
EXISTS
(SELECT 1 FROM UI_MON_HDR_V MH WHERE MH.CLAIMANT_ID = CLM.CLAIMANT_ID AND MH.CLAIM_ID = CLM.CLAIM_ID  AND MH.PROGRAM_ID = 3949 AND MON_DET_STATUS_CD = 'ACTV'
))
SELECT /*+PARALLLEL(8)*/ TO_CHAR(AP.RQST_WK_DT) "RQST_WK_DT",TO_CHAR(COUNT(DISTINCT AP.CLAIMANT_ID),'999,999') "PEUC_CLMT_CNT", 
TO_CHAR(SUM(NVL(AP.AUTH_AM,0)),'$999,999,999.00')  "TOT_AUTH_AM",
TO_CHAR(NVL(COUNT(DISTINCT PU.CLAIMANT_ID),0),'999,999') "PUA_CLMTS_WITH_PEUC_CNT"
FROM UI_AUTH_PMT_V AP, PEUC_DATA  PP, UI_EXTERNAL_PUA_WK_V PU
WHERE AP.CLAIMANT_ID = PP.CLAIMANT_ID
AND AP.PROGRAM_ID = 3949 
AND AP.STATUS_CD = 'PROC'
AND AP.CLAIMANT_ID = PU.CLAIMANT_ID(+)
AND AP.RQST_WK_DT+6 = PU.RQST_WK_DT(+)
GROUP BY  AP.RQST_WK_DT
HAVING SUM(AP.AUTH_AM) > 0
ORDER BY AP.RQST_WK_DT DESC 
"""


# Connect as user "hr" with password "welcome" to the "oraclepdb" service running on this computer.

#DVCI
conn = cx_Oracle.connect("ufactsapp", "XXXXXXX", "uicdvr01")

cursor = conn.cursor()

def f_Results(msg1,msg2,msgX,sql):
    global msg
    global number_of_rows
    global response
    number_of_rows = cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) > 0:
  
     if msgX == '### #Claim-Stats':
        for row in result:
        
         if (row[0] != '10: {03/01 - 03/07}'):  
          
           if  float(row[2].replace('%','')) < 0:
              x = '↓'
           else:
              x = '↑'
           if  float(row[4].replace('%','')) < 0:
              y = '↓'
           else:
              y = '↑'
           if  float(row[6].replace('%','')) < 0:
              z = '↓'
           else:
              z = '↑'     
           row = row[:2]+(row[2]+x,)+(row[3],)+(row[4]+y,)+(row[5],)+(row[6]+z,)+row[7:]
           str = '\t|'.join(row)
           msg = msg+'\n'+'|'+str+'|'
         else:
           row = row[:2]+('↑',)+(row[3],)+('↑',)+(row[5],)+('↑',)+row[7:]  
           str = '\t|'.join(row)
           msg = msg+'\n'+'|'+str+'|' 
     else:
         for row in result:
           str = '\t|'.join(row)
           msg = msg+'\n'+'|'+str+'|' 
    else:
        msg2 = ''
        msg =  ''
    message =  msg1+msg2+msg
    data = {"text":  msgX}
    response = requests.post(webhook_url, json=data)
    #print(message)
    #if (message.count > 0):
    data = {"text":  message}
    response = requests.post(webhook_url, json=data)
 


"""
number_of_rows = cursor.execute(sql)
result = cursor.fetchall()
for row in result:
    str = '\t|'.join(row)
    msg = msg+'\n'+'|'+str+'|'   
#pars = {"T_table":'UI_RECORD_SEARCH_V'}
"""    
"""
df = pd.DataFrame(result)
df = print(df.head(40))
print(df)
style.use('ggplot')
"""
#f = foo.users.get_user_by_username('sunil')
#print(f)
#print(url + endpoint)
#d = foo.status.get_user_status('o4zinmem1td3bkwhpx1cwmybrw')
#print(d)
msgX = '### #Claim-Stats'
msg1 = '| WEEK  | INITIAL  | INIT_PCT | REOPENED  | REOP_PCT | CONTINUED | CONT_PCT |'
msg2 = '\n | :------------ |:---------------:| -----:|:---------------:| -----:|:---------------:| -----:|'
msg =''
f_Results(msg1,msg2,msgX,claims_sql)

msgX = '### #SSA-Stats'
msg1 = '| DATE  | NEW_CLMT_CNT  | SSA_AUTH_Y |  SSA_AUTH_N |  SSA_AUTH_N_PCT |  SSA_DOWN_PEND_ISS|  SSA_DOWN_PEND_PCT|'
msg2 = '\n | :------------ |:---------------:| ---------------:|:---------------:|:---------------:|:---------------:| ---------------:|'
msg =''
f_Results(msg1,msg2,msgX,ssa_sql)


msgX = '### #FPUC-Stats'
msg1 = '| RQST_WK_DT  | CLMT_RCVD_FPUC_CNT  | TOT_AUTH_AM |'
msg2 = '\n | :------------ |:---------------:| ---------------:|'
msg =''
f_Results(msg1,msg2,msgX,fpuc_sql)

msgX = '### #PEUC-Stats'
msg1 = '| RQST_WK_DT  | PEUC_CLMT_CNT  | TOT_AUTH_AM | PUA_CLMTS_WITH_PEUC_CNT |'
msg2 = '\n | :------------ |:---------------:| :---------------:| ---------------:|'
msg =''
f_Results(msg1,msg2,msgX,peuc_sql)




"""
foo.posts.create_post(options={
    'channel_id': '5q6u9yb7wpb1j84i568zwq66br',   
    #'message': msg1+msg2+msg
    'message': 'This is test'
    ,
     })
"""
#message =  'This is test'
#print(message)
"""
foo.posts.create_post(options={
    'user_id': 'o4zinmem1td3bkwhpx1cwmybrw',   
    'url': 'https://www.website.info/mattermost/hooks/XXXXXXXXXXX',
    #'message': msg1+msg2+msg
    'message': 'This is test'
    ,
     })
"""


conn.close()

#print(cmd)
#os.system(cmd)
"""
pdf = df.pivot(index='CLAIM_TYPE', columns='WEEK', values='COUNT')
pdf.plot(kind='bar', stacked=False, title='Claims Stats', figsize=(8, 6),color=['red', 'green', 'orange', 'darkred', 'brown', 'pink', 'lightgreen', 'cyan', 'blue','yellow'])
data = {"text": plt.show()}
response = requests.post(webhook_url, json=data)
    #plt.show()

"""    
"""
if __name__ == '__main__':
    style.use('ggplot')
    df = df.head(10)
    pdf = df.pivot(index='CLAIM_TYPE', columns='WEEK', values='COUNT')
    print (pdf.head(40))
    #pdf.plot(kind='bar', stacked=False, title='Batch Run', figsize=(8, 6),color=['red', 'green', 'orange', 'darkred', 'brown', 'pink', 'lightgreen', 'cyan', 'blue','yellow'])
    #plt.show()
    conn.close()
"""    
