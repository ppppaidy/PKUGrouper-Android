from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from django.utils import timezone
from .someFuncs import *

import datetime

def datetime_earlier(dt1,dt2):
    diff = dt1-dt2
    return diff.days<0
    
def datetime_eq_or_earlier(dt1,dt2):
    return not datetime_earlier(dt2,dt1)
    
def get_misssion_state(mission):
    time_now = datetime.datetime.now()
    if datetime_earlier(time_now,mission.publishTime):
        return 'invaild publish time'
    if datetime_earlier(time_now,mission.applicationEndTime):
        return 'in application'
    if datetime_earlier(time_now,mission.executionStartTime):
        return 'between application and execution'
    if datetime_earlier(time_now,mission.executionEndTime):
        return 'in execution'   
    return 'finished'
    
'''
def mission_time_validity(old_mission,new_mission):
    if datetime_eq_or_earlier(new_mission.applicationEndTime,old_mission.publishTime):
        return False
    if datetime_earlier(new_mission.executionStartTime,new_mission.applicationEndTime):
        return False
    if datetime_eq_or_earlier(new_mission.executionEndTime,new_mission.executionStartTime):
        return False
    time_now = datetime.datetime.now()
    if (new_mission.applicationEndTime != old_mission.applicationEndTime) and 
       (datetime_earlier(new_mission.applicationEndTime,time_now)):
        return False
    if (new_mission.executionStartTime != old_mission.executionStartTime) and 
       (datetime_earlier(new_mission.executionStartTime,time_now)):
        return False
    if (new_mission.executionEndTime != old_mission.executionEndTime) and 
       (datetime_earlier(new_mission.executionEndTime,time_now)):
        return False
    return True
'''
def mission_to_json(mission):
    js = {
    "title" : mission.title,
    "content" : mission.content,
    "publisherID" : mission.publisher.id,
    "memberIDs" : list(map(lambda x:x.id,mission.members.all())),
    "applicantIDs" : list(map(lambda x:x.id,mission.applicants.all())),
    "state": get_mission_state(mission),
    "publishTime" : mission.publishTime.isoformat(sep=' '), 
    "applicationEndTime" : mission.applicationEndTime.isoformat(sep=' '),
    "executionStartTime" : mission.executionStartTime.isoformat(sep=' '),
    "executionEndTime" : mission.executionEndTime.isoformat(sep=' '),
    "channels" : list(map(lambda x:x.content,mission.applicants.all()))
    }
    return js
    
def string_to_datetime(s):
    return datetime.strptime(s,"%Y-%m-%d %H%M%S")
'''
好像暂时用不到或者说不好用
def json_to_mission(js):
'''
class DealMission(APIView):
    @staticmethod
    def get(request, user_ID, mission_ID):#获取任务信息
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        return Response(mission_to_json(which))

    @staticmethod
    def put(request, user_ID, mission_ID):#修改任务请求
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        #request body:mission
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
            
        new_applicationEndTime=string_to_datetime(request.body["applicationEndTime"])
        new_executionStartTime=string_to_datetime(request.body["executionStartTime"])
        new_executionEndTime=string_to_datetime(request.body["executionEndTime"])
        
        if datetime_eq_or_earlier(new_applicationEndTime,mission.publishTime):
            return Response("invalid Time",status=400)
        if datetime_earlier(new_executionStartTime,new_applicationEndTime):
            return Response("invalid Time",status=400)
        if datetime_eq_or_earlier(new_executionEndTime,new_executionStartTime):
            return Response("invalid Time",status=400)
        time_now = datetime.datetime.now()
        if (new_applicationEndTime != mission.applicationEndTime) and (datetime_earlier(new_applicationEndTime,time_now)):
            return Response("invalid Time",status=400)
        if (new_executionStartTime != mission.executionStartTime) and (datetime_earlier(new_executionStartTime,time_now)):
            return Response("invalid Time",status=400)
        if (new_executionEndTime != mission.executionEndTime) and (datetime_earlier(new_executionEndTime,time_now)):
            return Response("invalid Time",status=400)
            
        which.content=request.body["content"]
        which.title=request.body["title"]
        which.applicationEndTime=new_applicationEndTime
        which.executionStartTime=new_executionStartTime
        which.executionEndTime=new_executionEndTime
        which.channels.all().delete()
        for channelcontent in request.body["channels"]:
            try:
                channel = Channel.objects.get(content=channelcontent)
            except Channel.DoesNotExist:
                channel = Channel.objects.create(content=channelcontent)
            which.channels.add(channel)
        which.save(update_fields=['title','content','applicationEndTime','executionStartTime','executionEndTime','channels'])
        return Response('OK')

class DealMissions(APIView):#获取任务列表{tag+关键词}
    @staticmethod
    def get(request, user_ID):#request body:tag+关键词 List
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        result=Mission.objects.filter(id=0)#empty
        
        if (not(request.body["channels"]))and(not(request.body["keywords"])):
            result=Mission.objects.all()
        else:
            for channelcontent in request.body["channels"]:
                try:
                    channel = Channel.objects.get(content=channelcontent)
                    tmpset=Mission.objects.filter(channels=channel)
                    result=result | tmpset
                except:
                    a=1
                    
            for keywordscontent in request.body["keywords"]:
                tmpset = Mission.objects.filter(title__contains=keywordscontent)
                result=result | tmpset

            for keywordscontent in request.body["keywords"]:
                tmpset = Mission.objects.filter(content__contains=keywordscontent)
                result=result | tmpset
            
            result.distinct()
        startNumber=min(request.body["startNumber"]-1,len(result))
        endNumber=min(request.body["endNumber"],len(result))
        return Response(result[startNumber:endNumber])

class DealCreate(APIView):#创建任务请求
    @staticmethod
    def post(request, user_ID):#request body:mission
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        new_applicationEndTime=string_to_datetime(request.body["applicationEndTime"])
        new_executionStartTime=string_to_datetime(request.body["executionStartTime"])
        new_executionEndTime=string_to_datetime(request.body["executionEndTime"])
        
        time_now = datetime.datetime.now()
        if datetime_eq_or_earlier(new_applicationEndTime,time_now):
            return Response("invalid Time",status=400)
        if datetime_earlier(new_executionStartTime,new_applicationEndTime):
            return Response("invalid Time",status=400)
        if datetime_eq_or_earlier(new_executionEndTime,new_executionStartTime):
            return Response("invalid Time",status=400)
            
        which.content=request.body["content"]
        which.title=request.body["title"]
        which.applicationEndTime=new_applicationEndTime
        which.executionStartTime=new_executionStartTime
        which.executionEndTime=new_executionEndTime
        which.channels.all().delete()
        which.members.all().delete()
        which.applicants.all().delete()
        
        for channelcontent in request.body["channels"]:
            try:
                channel = Channel.objects.get(content=channelcontent)
            except Channel.DoesNotExist:
                channel = Channel.objects.create(content=channelcontent)
            which.channels.add(channel)
            
        which.publisher=who
        which.members.add(who)
        which.add()
        return Response('OK')

class DealDelete(APIView):#删除任务请求
    @staticmethod
    def post(request, user_ID, mission_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        which.delete()
        return Response("OK")

class DealJoin(APIView):#加入任务请求
    @staticmethod
    def post(request, user_ID, mission_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.applicationEndTime:
            return Response("Forbidden",status=403)
        if which.applicants.filter(user=who).count() > 0:
            return Response("Forbidden",status=403)
        if which.members.filter(user=who).count() > 0:
            return Response("Forbidden",status=403)
        tmpapp = Applicantship(user = who,mission = which)
        tmpapp.add()
        return Response("OK")

class DealAccept(APIView):#接受申请者请求
    @staticmethod
    def post(request, user_ID, mission_ID, applicant_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.applicationEndTime:
            return Response("Forbidden",status=403)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        try:
            tmpapp = Applicantship.gets(id=applicant_ID)
            if tmp.app.mission != which:
                return Response("Forbidden",status=403)
            tmpmem=Membership(user=tmpapp.user,mission=tmpapp.mission)
            tmpmem.add()
            tmpapp.delete()
            return Response("OK")
        except Applicantship.DoesNotExist:
            return Response("applicant Not Found",status=404)
        return Response("Unknown Fault",status=403)
        
class DealReject(APIView):#拒接申请者请求
    @staticmethod
    def post(request, user_ID, mission_ID, applicant_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.applicationEndTime:
            return Response("Forbidden",status=403)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        try:
            tmpapp = Applicantship.gets(id=applicant_ID)
            if tmp.app.mission != which:
                return Response("Forbidden",status=403)
            tmpapp.delete()
            return Response("OK")
        except Applicantship.DoesNotExist:
            return Response("applicant Not Found",status=404)
        return Response("Unknown Fault",status=403)
        
class DealFire(APIView):#踢出成员请求
    @staticmethod
    def post(request, user_ID, mission_ID, member_ID):#modified by hzq
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            member = User.objects.get(id=member_ID)
        except User.DoesNotExist:
            return Response("member Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.executionEndTime:#may need modification
            return Response("Forbidden",status=403)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        if member.id == which.publisher.id:
            return Response("Forbidden",status=403)
        try:
            tmpmem=Membership.objects.gets(mission=which,user=member)
            tmpmem.delete()
            return Response("OK")
        except Membership.DoesNotExist:
            return Response("Forbidden",status=404)
        return Response("Unknown Fault",status=403)

class DealStart(APIView):#开始任务
    @staticmethod
    def post(request, user_ID, mission_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.executionBeginTime:
            return Response("Forbidden",status=403)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        which.executionBeginTime=datetime.datetime.now()
        which.save()
        return Response("OK")

class DealFinish(APIView):#结束任务
    @staticmethod
    def post(request, user_ID, mission_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.executionEndTime:
            return Response("Forbidden",status=403)
        if who.id != which.publisher.id:
            return Response("Forbidden",status=403)
        which.executionEndTime=datetime.datetime.now()
        which.save()
        return Response("OK")

class DealQuit(APIView):#退出任务请求
    @staticmethod
    def post(request, user_ID, mission_ID):
        uid = checkUID(request.data)
        if uid is 0:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            return Response("User Not Found", 404)
        try:
            who = User.objects.get(id=user_ID)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)
        try:
            which = Mission.objects.get(id=mission_ID)
        except Mission.DoesNotExist:
            return Response("misssion Not Found",status=404)
        if datetime.datetime.now() > which.executionEndTime:#may need modification
            return Response("Forbidden",status=403)
        try:
            tmpmem=Membership.objects.gets(mission=which,user=who)
            tmpmem.delete()
            return Response("OK")
        except Membership.DoesNotExist:
            return Response("Forbidden",status=404)
        return Response("Unknown Fault",status=403)