from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from django.utils import timezone
from .someFuncs import *
import datetime
import random
import time


def fixtime(s):
    x = s.find('.')
    if x == -1:
        return s
    return s[:x]


def evaluation_to_json(evaluation):
    js = {
        "timeStamp": fixtime(str(evaluation.timeStamp)),
        "evaluaterID": evaluation.evaluater.id,
        "evaluateeID": evaluation.evaluatee.id,
        "missionID": evaluation.mission.id,
        "evaluationScore": evaluation.evaluationScore
    }
    return js


class DealSelf(APIView):  # 获取个人信息
    @staticmethod
    def post(request, user_ID):
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            response = Response("User Not Found", 404)
        elif uid != user_ID:
            return Response("Unauthorized", 401)
        else:
            user = User.objects.get(id=uid)
            mailbox = user.mailbox
            username = user.username
            tele = user.tele
            missions = []
            for mission in user.missionsAsPublisher.all():
                missions.append(mission.id)
            for mission in user.missionsAsMember.all():
                missions.append(mission.id)
            for mission in user.missionsAsApplicant.all():
                missions.append(mission.id)
            missions = list(set(missions))
            missions.sort(reverse=True)
            evaluations = []
            score = 0
            for evaluation in user.evaluationsAsEvaluatee.all():
                evaluations.append(evaluation.id)
                score += evaluation.evaluationScore
            if user.evaluationsAsEvaluatee.all().count() is not 0:
                score /= user.evaluationsAsEvaluatee.all().count()
            violations = []
            for message in user.messagesAsReportee.all():
                violations.append(message.id)
            data = {"mailbox": mailbox, "username": username, "tele": tele, "missionIDs": missions,
                    "valuationIDs": evaluations, "violationIDs": violations, "averageScore": score, "id": uid}
            response = Response(data, 200)
        return response


class DealMember(APIView):  # 获取他人信息
    @staticmethod
    def post(request, getter_ID, mission_ID, gettee_ID):  # geter是获取人，getee是被获取人
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif uid != getter_ID:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=getter_ID).count() == 0:
            response = Response("getter Not Found", 404)
        elif Mission.objects.filter(id=mission_ID).count() == 0:
            response = Response("mission Not Found", 404)
        elif User.objects.filter(id=gettee_ID).count() == 0:
            response = Response("gettee Not Found", 404)
        elif gettee_ID == getter_ID:
            response = Response("Bad Request", 400)
        elif Mission.objects.get(id=mission_ID).members.filter(id=gettee_ID).count() is 0 \
                and Mission.objects.get(id=mission_ID).publisher.id is not gettee_ID \
                and Mission.objects.get(id=mission_ID).applicants.filter(id=gettee_ID).count() is 0:
            response = Response("Forbidden", 403)
        else:
            gettee = User.objects.get(id=gettee_ID)
            mission = Mission.objects.get(id=mission_ID)
            score = 0
            name = gettee.username
            evaluations = []
            for evaluation in gettee.evaluationsAsEvaluatee.all():
                score += evaluation.evaluationScore
                evaluations.append(evaluation.id)
            if gettee.evaluationsAsEvaluatee.all().count() is not 0:
                score /= gettee.evaluationsAsEvaluatee.all().count()
            if mission.members.filter(id=getter_ID).count() is not 0 \
                    or mission.publisher.id is getter_ID:
                tele = gettee.tele
                data = {"missionStatus": "tele can be seen", "tele": tele, "averageScore": score, "username": name, "evaluationIDs": evaluations}
                response = Response(data, 200)
            else:
                data = {"missionStatus": "tele can not be seen", "averageScore": score, "username": name, "evaluationIDs": evaluations}
                response = Response(data, 200)
        return response


class DealEvaluations(APIView):  # 获取用户做过的所有评价
    @staticmethod
    def post(request, user_ID):
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            response = Response("user Not Found", 404)
        elif uid != user_ID:
            return Response("Unauthorized", 401)
        else:
            user = User.objects.get(id=user_ID)
            evaluations = []
            for evaluation in user.evaluationsAsEvaluater.all():
                evaluations.append(evaluation.id)
            response = Response(evaluations, 200)
        return response


class DealEvaluation(APIView):  # 根据evaluation_ID获取评价
    @staticmethod
    def post(request, evaluation_ID):
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif Evaluation.objects.filter(id=evaluation_ID).count() == 0:
            response = Response("evaluation Not Found", 404)
        else:
            response = Response(evaluation_to_json(Evaluation.objects.get(id=evaluation_ID)), 200)
        return response


class DealInfo(APIView):  # 修改个人信息
    @staticmethod
    def put(request, user_ID):  # request body:user
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            response = Response("User Not Found", 404)
        elif uid != user_ID:
            return Response("Unauthorized", 401)
        else:
            user = User.objects.get(id=user_ID)
            username = request.data.get('username', "")
            tele = request.data.get('tele', "")
            if username == "" or type(username) != str or tele == "" or type(tele) != str:
                response = Response("Bad Request", 400)
            else:
                user.username = username
                user.tele = tele
                user.save()
                response = Response("OK", 200)
        return response


class DealCode(APIView):  # 修改密码
    @staticmethod
    def put(request, user_ID):  # request body:password
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif User.objects.filter(id=user_ID).count() == 0:
            response = Response("User Not Found", 404)
        elif uid != user_ID:
            return Response("Unauthorized", 401)
        else:
            user = User.objects.get(id=user_ID)
            passwordAfterRSA = request.data.get('newPasswordAfterRSA', "")
            if passwordAfterRSA == "" or type(passwordAfterRSA) != str:
                response = Response("Bad Request", 400)
            else:
                user.passwordAfterMD5 = passwordToMD5(RSAdecypt(passwordAfterRSA))
                user.save()
                response = Response("OK", 200)
        return response


class DealEvaluate(APIView):  # 评分
    @staticmethod
    def post(request, evaluater_ID, mission_ID, evaluatee_ID):  # evaluater是评分人，evaluatee是被评分人
        uid = checkUID(request.data)
        if uid is 0:
            response = Response("Unauthorized", 401)
        elif uid != evaluater_ID:
            return Response("Unauthorized", 401)
        elif User.objects.filter(id=evaluater_ID).count() == 0:
            response = Response("evaluater Not Found", 404)
        elif Mission.objects.filter(id=mission_ID).count() == 0:
            response = Response("mission Not Found", 404)
        elif User.objects.filter(id=evaluatee_ID).count() == 0:
            response = Response("evaluatee Not Found", 404)
        elif evaluatee_ID == evaluater_ID:
            response = Response("Forbidden", 403)
        elif request.data.get('score', -1) == -1 or request.data.get('score', -1) < 0\
                or request.data.get('score', -1) > 10:
            response = Response("Forbidden", 403)
        else:
            #  judge whether this evaluation has been made once
            mission = Mission.objects.get(id=mission_ID)
            evaluater = User.objects.get(id=evaluater_ID)
            evaluatee = User.objects.get(id=evaluatee_ID)
            if evaluatee.evaluationsAsEvaluatee.filter(evaluater=evaluater).count() != 0 and\
                evaluatee.evaluationsAsEvaluatee.filter(mission=mission).count() != 0:
                response = Response("Forbidden", 403)
            elif mission.publisher.id != evaluater_ID and mission.members.filter(id=evaluater_ID).count() == 0:
                response = Response("Forbidden", 403)
            elif mission.publisher.id != evaluatee_ID and mission.members.filter(id=evaluatee_ID).count() == 0:
                response = Response("Forbidden", 403)
            else:
                Evaluation.objects.create(evaluationScore=request.data.get('score'), timeStamp=datetime.datetime.now(),
                                          evaluater=evaluater, evaluatee=evaluatee, mission=mission)
                response = Response("OK", 200)
        return response


# This is omitted for now
class DealTags(APIView):#修改tagList
    @staticmethod
    def put(request, user_ID):#request body:tagList
        return Response(['This is a PUT of user/tags/{user_ID}', request.data])


class DealCaptcha(APIView):#获取验证码
    @staticmethod
    def post(request):#request body:user(regiter information only)
        #return Response(['This is a POST of user/captcha', request.data])
        mail = request.data.get("mailbox")
        if User.objects.filter(mailbox=mail).count()!=0:
            return Response("BadRequest", status=400)
        try:
            captcha = Captcha.objects.get(mailbox=mail)
        except:
            captcha = Captcha(mailbox=mail,
                              captchaContent=''.join([str(random.randint(0,9)) for i in range(6)]))
            captcha.save()
        if datetime.datetime.now()-captcha.timeStamp > datetime.timedelta(seconds=300):
            captcha.captchaContent = ''.join([str(random.randint(0,9)) for i in range(6)])
        captcha.save()
        if sendMail(mail, captcha.captchaContent)==0:
            return Response("BadRequest",status=400)
        else:
            return Response("OK")

class DealRegister(APIView):#注册
    @staticmethod
    def post(request):#request body:user(regiter information only)
        #return Response(['This is a POST of user/register', request.data])
        mail = request.data.get("mailbox")
        passwordAfterRSA = request.data.get("passwordAfterRSA")
        captchaCode = request.data.get("captchaCode")
        username = request.data.get("username")
        if User.objects.filter(username=username).count() > 0:
            return Response("bad username",status=400)
        if Captcha.objects.filter(mailbox=mail).count() == 0:
            return Response("Do not have captcha!",status=400)
        captcha = Captcha.objects.get(mailbox=mail)
        if datetime.datetime.now()-captcha.timeStamp > datetime.timedelta(seconds=300):
            return Response("captcha time limit exceed!",status=400)
        if captcha.captchaContent != captchaCode:
            return Response("captchaCode wrong!",status=400)
        md5code = passwordToMD5(RSAdecypt(passwordAfterRSA))
        person = User(username=username, mailbox=mail, passwordAfterMD5=md5code)
        person.save()
        captcha.delete()
        return Response({"UID":person.id})

class DealLogin(APIView):#登录
    @staticmethod
    def post(request):#request body:user(login information only)
        #return Response(['This is a POST of user/login', request.data])
        mail = request.data.get("mailbox")
        passwordAfterRSA = request.data.get("passwordAfterRSA")
        if mail == None or passwordAfterRSA == None:
            Response("info not complete",status=403)

        try:
            who = User.objects.get(mailbox=mail)
        except User.DoesNotExist:
            return Response("user Not Found",status=404)

        code = passwordToMD5(RSAdecypt(passwordAfterRSA))
        if who.passwordAfterMD5 != code:
            return Response("Forbidden",status=404)
        return Response({"UID":who.id})

class DealFixPasswordCaptcha(APIView):#找回密码之获取验证码
    @staticmethod
    def post(request):
        mail = request.data.get("mailbox")
        if User.objects.filter(mailbox=mail).count()==0:
            return Response("BadRequest", status=400)
        try:
            captcha = Captcha.objects.get(mailbox=mail)
        except:
            captcha = Captcha(mailbox=mail,
                              captchaContent=''.join([str(random.randint(0,9)) for i in range(6)]))
            captcha.save()
        if datetime.datetime.now()-captcha.timeStamp > datetime.timedelta(seconds=300):
            captcha.captchaContent = ''.join([str(random.randint(0,9)) for i in range(6)])
        captcha.save()
        if sendMail(mail, captcha.captchaContent)==0:
            return Response("BadRequest",status=400)
        else:
            return Response("OK")

class DealFixPassword(APIView):#找回密码
    @staticmethod
    def post(request):
        mail = request.data.get("mailbox")
        passwordAfterRSA = request.data.get("passwordAfterRSA")
        captchaCode = request.data.get("captchaCode")
        if Captcha.objects.filter(mailbox=mail).count() == 0:
            return Response("Do not have captcha!",status=400)
        if User.objects.filter(mailbox=mail).count() == 0:
            return Response("Bad Request", status=400)
        captcha = Captcha.objects.get(mailbox=mail)
        if datetime.datetime.now()-captcha.timeStamp > datetime.timedelta(seconds=300):
            return Response("captcha time limit exceed!",status=400)
        if captcha.captchaContent != captchaCode:
            return Response("captchaCode wrong!",status=400)
        md5code = passwordToMD5(RSAdecypt(passwordAfterRSA))
        person = User.objects.get(mailbox=mail)
        person.passwordAfterMD5 = md5code
        person.save()
        captcha.delete()
        return Response({"UID":person.id})
