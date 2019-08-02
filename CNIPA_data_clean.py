import os
import sys
import time
import pandas as pd
import numpy as np

project_path = os.path.abspath(os.path.dirname(sys.argv[0]))
data_709_name_list = ['CN_patent_invention_published_709', 'CN_patent_invention_authorized_709',
                  'CN_patent_utility_new_709', 'CN_patent_appearance_designed_709']
data_712_name_list = ['CN_patent_invention_published_712', 'CN_patent_invention_authorized_712',
                  'CN_patent_utility_new_712', 'CN_patent_appearance_designed_712']
attr_name_list = ['item', 'name', 'authorization_notice_id', 'authorized_announcement_date',
                  'filing_id', 'filing_date', 'patentee', 'designer','address', 'Int.Cl.']
patentee_type_dict = {0: ['学校', '学院', '大学', '中学', '小学'],
                      1: ['研究所', '研究', '中心', '科技', '设计', '技术', '研究技术指导所', '地质勘查院', '学会', '测绘院', '基地', '实验室'],
                      2: ['公司', '会社', '集团', '合作社','企业', '工作室', '赛峰航空器发动机', '阿尔卡特朗讯', '赛峰航空器发动机', '路易威登马利蒂',
                          'GN瑞声达A/S', '现代岱摩斯', '协进连接器', '虚拟现实软件', '法国德西尼布'],
                      3: ['工厂', '厂', '工场'],
                      4: ['部队',],
                      # 5: ['党政机关', '检验院', '分支机构', '电业局', '地质调查院', '设备经销处', '航空器发动机', '交通管理支队', '地震局', '公安局', '税务局',
                      #     '事务所', '管理处', '水务局', '监督所', '检测所', '人力资源和社会保障局', '检验所', '气象局', '动物园', '植物园', '街道办事处', '打捞局', '专卖局'],
                      5: ['党政机关', '检验院','调查院', '监测院', '分支机构', '处', '局', '所', '园', '站', '办公室', '服务部'],
                      6: ['医院', '病院','保健院', '防治院'],
                      7: ['社会团体', '委员会','基金会', '机构', '协会',],
                      8: ['农业', '家庭农场', '养殖场', '茶场', '渔业', '水利工程', '农庄', '畜场'],
                      9: ['个体经营', '烘焙店', '门市部', '休闲山庄', '汽车实业', '商行'],
                      10: ['个人', '比克-维尔莱克', '阿南塔南达努腊', '那顺吉日嘎', '安纳特思科']}
incorrect_link_list = [';??', ';']
IPC_classificaion = {'A':'人类生活必需','B':'作业；运输','C':'化学；冶金','D':'纺织；造纸',
                     'E':'固定建筑物','F':'机械工程；照明；加热；武器；爆破','G':'物理','H':'电学'}
LOC_classificaion = {'01': '食品', '02': '服装和服饰物件', '03': '旅行用具,箱盒,阳伞和个人物品 (不属别类的)', '04': '刷具', '05': '纺织物件,人造和天然材料之片材类',
                    '06': '家具', '07': '家用物品 (不属别类的)', '08': '工具和五金器材', '09': '用於运输或处理货物的包装和容器', '10': '钟,手表和其他计测仪器', '11': '装饰物件',
                    '12': '运输或升降的工具', '13': '电力生产,分配或变压的设备', '14': '录制,通讯或资讯起复的设备', '15': '机具(不属别类的)', '16': '照相,电影和光学装置',
                    '17': '乐器', '18': '印刷和办公室机器', '19': '文具和办公设备,美术用品和教学材料', '20': '销售和广告设备,标志', '21': '游戏,玩具,帐篷和运动货品',
                    '22': '武器,火药用品,以及狩猎,钓鱼和灭虫的用具', '23': '液体分配设备,卫生,供热,通风和空调设备,固体燃料', '24': '医疗和实验室设备',
                    '25': '建筑物单位和建筑元素', '26': '照明装置', '27': '烟草和烟具', '28': '药品和化妆用品,梳洗用品和装置', '29': '防火救援,预防事故和救生的装置和设备',
                    '30': '护理动物的用品', '31': '食品或饮料制作的机器和器具(不属别类的)'}


"""编码从('GB18030')改成UTF8"""
def csvTypeChange(data_name):
    target_data = pd.read_csv(project_path+"\\data_from_html\\"+data_name+'.csv',encoding=('GB18030'))
    target_data.to_csv(project_path+"\\data_from_html\\Intermediate_File\\UTF8_"+data_name+".csv", index=False, encoding = "UTF8")
"""根据专利授权公告号查询覆盖率"""
def coverageRate(data_name):
    target_data = pd.read_csv(project_path+"\\data_from_html\\Intermediate_File\\UTF8_"+data_name+'.csv',encoding="UTF8")
    authorization_published_id_list = list(target_data.authorization_notice_id)
    data_length = len(authorization_published_id_list)
    effect_authorization_published_id_list = list(set(authorization_published_id_list))
    data_effect_length = len(effect_authorization_published_id_list)
    print("数据完整度：{0}".format(data_effect_length/data_length))
    return data_effect_length/data_length
"""根据专利授权公告号生成无重数据表"""
def eliminateDuplicates(data_name):
    target_data = pd.read_csv(project_path+"\\data_from_html\\Intermediate_File\\UTF8_"+data_name+'.csv',encoding="UTF8")
    authorization_published_id_list = list(target_data.authorization_notice_id)
    data_length = len(authorization_published_id_list)
    effect_authorization_published_id_list = list(set(authorization_published_id_list))
    data_effect_length = len(effect_authorization_published_id_list)
    total_tag = np.zeros((data_effect_length,1))

    item_count = 0
    for item in range(data_length):
        authorization_published_id = target_data.authorization_notice_id.iloc[item]
        item_tag = effect_authorization_published_id_list.index(authorization_published_id)
        if total_tag[item_tag] != 0:
            continue
        else:
            total_tag[item_tag] += 1

        spider_list = [target_data[attr_name_list[item1]].iloc[item] for item1 in range(1, len(attr_name_list))]

        if item_count == 0:
            CN_patent = pd.DataFrame([target_data.authorization_notice_id.iloc[item]])
            CN_patent = CN_patent.rename(columns={0: 'authorization_notice_id'})
            CN_patent.insert(1, attr_name_list[1], spider_list[0])
            for i in range(3, 10):
                CN_patent.insert(i-1, attr_name_list[i], spider_list[i-1])
        else:
            spider_list1 = [spider_list[item] for item in [1, 0, 2, 3, 4, 5, 6, 7, 8]]
            attr_name_list1 = [attr_name_list[item] for item in [2, 1, 3, 4, 5, 6, 7, 8, 9]]
            insertRow = pd.DataFrame([spider_list1], columns=attr_name_list1)
            above = CN_patent.loc[:item_count]
            below = CN_patent.loc[item_count + 1:]
            CN_patent = above.append(insertRow, ignore_index=True).append(below, ignore_index=True)
        item_count += 1

    CN_patent.to_csv(project_path+"\\data_from_html\\Intermediate_File\\eliminate_duplicates_"+data_name+'.csv',encoding="UTF8", index=False)
    return CN_patent
"""申请日精确到月份，保存格式 '2015-12'"""
def uniformFilingDateToMonth(data_name):
    target_data = pd.read_csv(project_path + "\\data_from_html\\Intermediate_File\\eliminate_duplicates_" + data_name + '.csv', encoding="UTF8")
    new_filing_date = list(target_data.filing_date)
    new_filing_date = [date1.replace('.', '-')[:7] for date1 in new_filing_date]
    target_data = target_data.drop(['filing_date'], axis=1)
    target_data.insert(5,'filing_date', new_filing_date)

    target_data.to_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_filing_date_to_month_" + data_name + '.csv', encoding="UTF8", index=False)
    return target_data
"""清洗地址"""
# 分类1：外国，精确的国家
# 分类2：国内，精确到省份
def uniformAddress(data_name):
    target_data = pd.read_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_filing_date_to_month_" + data_name + '.csv', encoding="UTF8")
    provinces_data = pd.read_csv(project_path + "\\data_from_html\\ChinaProvinces.csv", encoding="GBK")
    country_data = pd.read_csv(project_path + "\\data_from_html\\country_info.csv", encoding="GBK")
    new_address = []
    tag = np.zeros((len(target_data), 1))
    count = 0
    for address in list(target_data.address):
        if address == '百慕大汉密尔顿':
            new_address.append('百慕大群岛')
            tag[count] = 1
            count += 1
            continue
        if address == '根西岛圣彼得港':
            new_address.append('英国')
            tag[count] = 1
            count += 1
            continue
        if address == '捷克奥尔利采河畔乌斯季':
            new_address.append('捷克共和国')
            tag[count] = 1
            count += 1
            continue

        for item in list(provinces_data.Name):
            if item in address or item[:2] in address:
                new_address.append(item)
                tag[count] = 1
                break
        if tag[count] != 1:
            for item in list(country_data.Label):
                if item in address:
                    new_address.append(item)
                    tag[count] = 1
                    break
        if tag[count] != 1:
            new_address.append(address)
        count += 1

    # full_address = [list(target_data.address)[item] for item in range(len(target_data)) if tag[item]==0]
    # print('未匹配地址的项：\n{0}\n'.format(full_address))

    target_data = target_data.drop(['address'], axis=1)
    target_data.insert(7,'address', new_address)

    target_data.to_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_address_" + data_name + '.csv', encoding="UTF8", index=False)
    return target_data
"""清洗专利权人"""
def uniformPatentee(data_name):
    target_data = pd.read_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_address_" + data_name + '.csv', encoding="UTF8")
    new_patentee_list = []
    tag = np.zeros((len(target_data), 1))
    count = 0

    # 剔除错误连接（使用'@'连接）
    correct_link_patentee_list = []
    link_count = 0

    for patentee in list(target_data.patentee):
        link_flag = True
        for item in incorrect_link_list:
            if item in patentee:
                correct_link_patentee_list.append(patentee.replace(item, '@'))
                link_count += 1
                link_flag = False
                break
        if link_flag == True:
            correct_link_patentee_list.append(patentee)
            link_count += 1

    patentee_count = 0
    patentee_type_content = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: []}
    for patentee in correct_link_patentee_list:

        # 除个人之外的机构类型
        count_flag = False
        for item1 in range(0,len(patentee_type_dict)-1):
            for item2 in patentee_type_dict[item1]:
                if item2 in patentee:
                    new_patentee_list.append(patentee_type_dict[item1][0])
                    tag[count] = 1
                    count += 1
                    count_flag = True
                    patentee_type_content[item1].append(patentee)
                    break
            if count_flag:
                break
        if count_flag:
            continue

        # 筛选出个人
        if len(patentee)==2 or len(patentee)==3 or len(patentee)==4 or '·' in patentee or '.' in patentee \
                or patentee in list(patentee_type_dict[10]):
            new_patentee_list.append('个人')
            tag[count] = 1
            count += 1
            patentee_type_content[len(patentee_type_dict)-1].append(patentee)
            continue


        # 筛选出多人合作
        holder_flag = True
        patentee = patentee.replace('\u2022', '')
        patentee_holder_list = patentee.split('@')

        for item in patentee_holder_list:
            if len(item) == 0 or len(item) == 2 or len(item) == 3 or len(item) == 4 or '·' in item or '.' in item:
                continue
            else:
                holder_flag = False
                break
        if holder_flag == True:
            new_patentee_list.append('个人')
            tag[count] = 1
            count += 1
            patentee_type_content[len(patentee_type_dict)-1].append(patentee_holder_list)
            continue

        new_patentee_list.append(patentee)
        count += 1



    # unmatched_patentee = [correct_link_patentee_list[item] for item in range(len(target_data)) if tag[item]==0]
    # print('未匹配的机构：\n{0}\n'.format(unmatched_patentee))
    # print(patentee_type_content[9])

    target_data = target_data.drop(['patentee'], axis=1)
    target_data.insert(7,'patentee', new_patentee_list)

    target_data.to_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_patentee_" + data_name + '.csv', encoding="UTF8", index=False)
    return target_data
"""清洗Int.Cl.（分类号）"""
# 分类1：IPC(发明公布、发明授权、实用新型)
# 分类2：LOC(外观设计)
def uniformIPC(data_name):
    target_data = pd.read_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_patentee_" + data_name + '.csv', encoding="UTF8")
    # IPC_LOC = target_data['Int.Cl.']
    # target_data = target_data.drop(['Int.Cl.'], axis=1)
    # target_data.insert(8,'IPC_LOC', IPC_LOC)
    new_IPC_list = []
    new_LOC_list = []
    tag = np.zeros((len(target_data), 1))
    count = 0

    # 剔除错误连接（使用'@'连接）
    correct_link_IPC_list = []
    link_count = 0

    for IPC in list(target_data["Int.Cl."]):
        link_flag = True
        for item in incorrect_link_list:
            if item in IPC:
                correct_link_IPC_list.append(IPC.replace(item, '@'))
                link_count += 1
                link_flag = False
                break
        if link_flag == True:
            correct_link_IPC_list.append(IPC)
            link_count += 1

    IPC_type_content = []
    LOC_type_content = []
    for IPC in correct_link_IPC_list:
        IPC = IPC.split('@')
        if data_name != 'CN_patent_appearance_designed_709' and data_name != 'CN_patent_appearance_designed_712':
            if len(IPC) == 1:
                location = list(IPC_classificaion.keys()).index(IPC[0][0])
                # new_IPC_list.append(IPC_classificaion[list(IPC_type_content.keys())[location]])
                new_IPC_list.append(list(IPC_classificaion.keys())[location])
                IPC_type_content.append([IPC])
                continue
            if len(IPC[1]) == 0:
                location = list(IPC_classificaion.keys()).index(IPC[0][0])
                new_IPC_list.append(list(IPC_classificaion.keys())[location])
                IPC_type_content.append(IPC[0])
                continue
            else:
                list1 = []
                list2 = []
                for item in IPC:
                    try:
                        location = list(IPC_classificaion.keys()).index(item[0])
                        if list(IPC_classificaion.keys())[location] not in list1:
                            list1.append(list(IPC_classificaion.keys())[location])
                        list2.append(item)
                    except Exception as e:
                        location = list(IPC_classificaion.keys()).index(item[1])
                        if list(IPC_classificaion.keys())[location] not in list1:
                            list1.append(list(IPC_classificaion.keys())[location])
                        list2.append(item)

                if len(list1) == 1:
                    new_IPC_list.append(list1[0])
                else:
                    new_IPC_list.append(list1)
                IPC_type_content.append(list2)

        else:
            LOC = IPC
            if len(LOC) == 1:
                location = list(LOC_classificaion.keys()).index(LOC[0][:2])
                # new_LOC_list.append(LOC_classificaion[list(LOC_type_content.keys())[location]])
                new_LOC_list.append(list(LOC_classificaion.keys())[location])
                LOC_type_content.append([LOC])
                continue
            if len(LOC[1]) == 0:
                location = list(LOC_classificaion.keys()).index(LOC[0][:2])
                # new_LOC_list.append(LOC_classificaion[list(LOC_type_content.keys())[location]])
                new_LOC_list.append(list(LOC_classificaion.keys())[location])
                LOC_type_content.append(LOC[0])
                continue
            else:
                list1 = []
                list2 = []
                for item in LOC:
                    try:
                        location = list(LOC_classificaion.keys()).index(item[:2])
                        if list(LOC_classificaion.keys())[location] not in list1:
                            list1.append(list(LOC_classificaion.keys())[location])
                        list2.append(item)
                    except Exception as e:
                        try:
                            location = list(LOC_classificaion.keys()).index(item[1])
                        except:
                            location = list(LOC_classificaion.keys()).index(item[1:3])
                        if list(LOC_classificaion.keys())[location] not in list1:
                            list1.append(list(LOC_classificaion.keys())[location])
                        list2.append(item)

                if len(list1) == 1:
                    new_LOC_list.append(list1[0])
                else:
                    new_LOC_list.append(list1)
                LOC_type_content.append(list2)


    target_data = target_data.drop(['Int.Cl.'], axis=1)
    try:
        target_data.insert(8,'IPC', new_IPC_list)
    except:
        target_data.insert(8, 'LOC', new_LOC_list)
    target_data.to_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_IPC_" + data_name + '.csv', encoding="UTF8", index=False)
    return target_data
"""保留有用部分"""
def keepUsefulPart(data_name):
    target_data = pd.read_csv(project_path + "\\data_from_html\\Intermediate_File\\uniform_IPC_" + data_name + '.csv',
                              encoding="UTF8")
    final_data = pd.DataFrame(target_data.authorization_notice_id)
    final_data = final_data.rename(columns={0: 'authorization_notice_id'})
    final_data.insert(1, 'filing_date', target_data.filing_date)
    final_data.insert(2, 'patentee', target_data.patentee)
    final_data.insert(3, 'address', target_data.address)
    try:
        final_data.insert(4, 'IPC', target_data.IPC)
    except:
        final_data.insert(4, 'LOC', target_data.LOC)
    final_data.to_csv(project_path + "\\data_from_html\\FINAL_" + data_name + '.csv', encoding="GBK",index=False)


def main():
    start_time = time.time()

    for item in range(len(data_709_name_list)):
        csvTypeChange(data_709_name_list[item])
        coverageRate(data_709_name_list[item])
        eliminateDuplicates(data_709_name_list[item])
        uniformFilingDateToMonth(data_709_name_list[item])
        uniformAddress(data_709_name_list[item])
        uniformPatentee(data_709_name_list[item])
        uniformIPC(data_709_name_list[item])
        keepUsefulPart(data_709_name_list[item])
    for item in range(len(data_712_name_list)):
        csvTypeChange(data_712_name_list[item])
        coverageRate(data_712_name_list[item])
        eliminateDuplicates(data_712_name_list[item])
        uniformFilingDateToMonth(data_712_name_list[item])
        uniformAddress(data_712_name_list[item])
        uniformPatentee(data_712_name_list[item])
        uniformIPC(data_712_name_list[item])
        keepUsefulPart(data_712_name_list[item])

    end_time = time.time()  # 结束时间
    cost_time = end_time - start_time  # 总运行时间，并按时分秒完成输出
    print('本次运行耗时：{0}时{1}分{2}秒 '.format(int(cost_time / 3600), int((cost_time / 60) % 60), int(cost_time % 60)))


if __name__ == '__main__':




    main()