package com.e.pkugrouper.Managers;

import com.alibaba.fastjson.JSONObject;
import com.e.pkugrouper.Models.IMessage;
import com.e.pkugrouper.Models.IMission;
import com.e.pkugrouper.Models.IUser;
import com.e.pkugrouper.Models.Mission;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class MissionManager extends HttpManager implements IMissionManager{

    private IUser currentUser;

    private final String user_not_found = "\"user Not Found\"";
    private final String mission_not_found = "\"mission Not Found\"";
    private final String bad_request = "\"Bad Request\"";
    private final String forbidden = "\"Forbidden\"";
    private final String ok = "\"OK\"";
    private final String invalid_time = "\"invalid time\"";
    private final String applicant_not_found = "\"applicant Not Found\"";
    @Override
    public void setCurrentUser(IUser _currentUser) {
        if (_currentUser == null){
            //report or throw
        }
        else
            currentUser = _currentUser;
    }

    @Override
    public IMission findMissionByID(int missionID) {
        //检查currentUser是否存在
        if(currentUser == null){
            //throw
            return null;
        }

        //检查参数
        if(missionID <= 0) {
            //report or throw
            return null;
        }

        //获得Mission的JSON序列
        String url = "/mission";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String Mission_JSON = httpGet(url, parameters, request_body.toJSONString());

        //未返回合法的mission的JSON序列
        if(Mission_JSON.equals(user_not_found)) {
            //report user not found
            return null;
        }
        else if(Mission_JSON.equals(mission_not_found)){
            //report mission not found
            return null;
        }

        IMission mission = new Mission();
        mission.loadFromJSON(Mission_JSON);
        return mission;
    }

    @Override
    public List<IMission> findMissionByDescription(String description, List<String> channels,
                                                   int startNumber, int endNumber) {
        //详细api文档中tags和keywords 这里是description和tags
        //检查currentUser是否为空
        if(currentUser == null){
            //throw
            return null;
        }

        //检查参数
        if(description == null || channels == null) {
            //report or throw
            return null;
        }

        //得到Mission的JSON序列
        String url = "/missions";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        request_body.put("channels", channels);
        String[] keywords = description.split(" ");
        request_body.put("keywords", keywords);
        request_body.put("startNumber", startNumber);
        request_body.put("endNumber", endNumber);
        String Missions_JSON = httpGet(url, parameters, request_body.toJSONString());

        //获取任务列表失败
        if(Missions_JSON.equals(user_not_found)) {
            //report user not found
            return null;
        }
        else if(Missions_JSON.equals(bad_request)){
            //bad request
            return null;
        }

        List<Integer> mission_id_list = JSONObject.parseArray(Missions_JSON, Integer.class);
        if(mission_id_list.size() == 0)
            return null;
        List<IMission> mission_list = new ArrayList<>();
        for(int mission_id: mission_id_list){
            IMission mission = findMissionByID(mission_id);
            if(mission != null)
                mission_list.add(mission);
        }
        return mission_list;
    }

    @Override
    public boolean deleteMission(int missionID) {
        //检查currentUser是否为空
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if (missionID <= 0) {
            //report or throw;
            return false;
        }

        //删除信息
        String url = "/mission/delete";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String delete_response = httpPost(url, parameters, request_body.toJSONString());

        if(delete_response.equals(ok)){
            //report
            return true;
        }

        if(delete_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(delete_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(delete_response.equals(forbidden)){
            //forbidden
            return false;
        }
        return false;
    }

    @Override
    public boolean addMission(IMission mission) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(mission == null) {
            //report or throw
            return false;
        }

        //添加Mission
        String url = "/mission/create";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        JSONObject mission_JSON = JSONObject.parseObject(mission.toJSON());
        request_body.putAll(mission_JSON);
        String add_response = httpPost(url, parameters, request_body.toJSONString());

        //创建任务失败
        if(add_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(add_response.equals(invalid_time)){
            //invalid time
            return false;
        }

        //创建任务成功
        JSONObject missionID = JSONObject.parseObject(add_response);
        mission.setID(missionID.getInteger("missionID"));
        return true;
    }

    @Override
    public boolean editMission(IMission mission) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(mission == null) {
            //report or throw
            return false;
        }

        //修改Mission
        String url = "/mission";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(mission.getID()));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        JSONObject mission_JSON = JSONObject.parseObject(mission.toJSON());
        request_body.putAll(mission_JSON);
        String edit_response = httpPut(url, parameters, request_body.toJSONString());

        if(edit_response.equals(ok)){
            return true;
        }

        if(edit_response.equals(user_not_found)){
            //report user not found;
            return false;
        }
        else if(edit_response.equals(mission_not_found)){
            //report mission not found
            return false;
        }
        else if(edit_response.equals(invalid_time)){
            //report invalid time
            return false;
        }

        return false;
    }

    @Override
    public boolean accept(int missionID, int applicantID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report invalid missionID
            return false;
        }

        if(applicantID <= 0) {
            //report invalid applicantID
            return false;
        }

        //接受成员
        String url = "/mission/accept";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID), String.valueOf(applicantID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String accept_response = httpPost(url, parameters, request_body.toJSONString());

        //接受成员成功
        if(accept_response.equals(ok)){
            //report accept success
            return true;
        }

        //接受成员失败
        if(accept_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(accept_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(accept_response.equals(applicant_not_found)){
            //applicant not found
            return false;
        }
        else if(accept_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }

    @Override
    public boolean fire(int missionID, int applicantID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report invalid missionID
            return false;
        }

        if(applicantID <= 0) {
            //report invalid applicantID
            return false;
        }

        //踢出参与者
        String url = "/mission/fire";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID), String.valueOf(applicantID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String fire_response = httpPost(url, parameters, request_body.toJSONString());

        //踢出成员成功
        if(fire_response.equals(ok)){
            //report accept success
            return true;
        }

        //踢出成员失败
        if(fire_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(fire_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(fire_response.equals(applicant_not_found)){
            //applicant not found
            return false;
        }
        else if(fire_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }

    @Override
    public boolean reject(int missionID, int applicantID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report invalid missionID
            return false;
        }

        if(applicantID <= 0) {
            //report invalid applicantID
            return false;
        }

        //拒绝参与者申请
        String url = "/mission/reject";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID), String.valueOf(applicantID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String reject_response = httpPost(url, parameters, request_body.toJSONString());

        //拒绝接受成员成功
        if(reject_response.equals(ok)){
            //report reject success
            return true;
        }

        //拒绝接受成员失败
        if(reject_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(reject_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(reject_response.equals(applicant_not_found)){
            //applicant not found
            return false;
        }
        else if(reject_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }

    @Override
    public boolean join(int missionID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report or throw
            return false;
        }

        //申请加入某个任务
        String url = "/mission/join";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String join_response = httpPost(url, parameters, request_body.toJSONString());

        //加入成功
        if(join_response.equals(ok)){
            //report join success
            return true;
        }

        //加入失败
        if(join_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(join_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(join_response.equals(forbidden)){
            //forbidden
            return false;
        }
        return false;
    }

    @Override
    public boolean quit(int missionID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report or throw
            return false;
        }

        //退出任务
        String url = "/mission/quit";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String quit_response = httpPost(url, parameters, request_body.toJSONString());

        //退出任务成功
        if(quit_response.equals(ok)){
            //report quit success
            return true;
        }

        //退出任务失败
        if(quit_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(quit_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(quit_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }

    @Override
    public boolean start(int missionID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report or throw
            return false;
        }

        //开始任务
        String url = "/mission/start";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String start_response = httpPost(url, parameters, request_body.toJSONString());

        //开始任务成功
        if(start_response.equals(ok)){
            //report start success
            return true;
        }

        //开始任务失败
        if(start_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(start_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(start_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }

    @Override
    public boolean finish(int missionID) {
        //检查currentUser
        if(currentUser == null){
            //throw
            return false;
        }

        //检查参数
        if(missionID <= 0) {
            //report or throw
            return false;
        }

        //结束任务
        String url = "/mission/finish";
        List<String> parameters = Arrays.asList(String.valueOf(currentUser.getUserID()),
                String.valueOf(missionID));
        JSONObject request_body = new JSONObject();
        request_body.put("senderID",currentUser.getUserID());
        request_body.put("passwordAfterRSA", currentUser.getPassword());
        String finish_response = httpPost(url, parameters, request_body.toJSONString());

        //结束任务成功
        if(finish_response.equals(ok)){
            //report finish success
            return true;
        }

        //结束任务失败
        if(finish_response.equals(user_not_found)){
            //user not found
            return false;
        }
        else if(finish_response.equals(mission_not_found)){
            //mission not found
            return false;
        }
        else if(finish_response.equals(forbidden)){
            //forbidden
            return false;
        }

        return false;
    }
}
