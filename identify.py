from deepface import DeepFace
import os, time

def verify(src_path, model, temp):
    start = time.time() 
    base_dir = os.getcwd()
    temp = float(temp)
    # print("현재 디렉토리는 {}".format(base_dir))
    num_list = os.listdir(os.path.join(base_dir, 'img_data'))
    # print(name_list)
    src_img = os.path.join(base_dir, src_path)
    # print(src_img)
    # 모든 폴더를 돌아가며 가장 첫번째 사진을 비교해서 
    # 각 이미지의 결과 리스트 중  verified값이 True인 경우엔 그 결과값을 res_list에 저장해준다.
    res_list = []
    for stu_num in num_list:
        data_list = os.listdir(os.path.join(base_dir, 'img_data', stu_num))
        res = DeepFace.verify(img1_path=src_img, 
                                img2_path=os.path.join(base_dir, 'img_data', stu_num, data_list[0]),
                                model_name = model,
                                distance_metric='euclidean_l2', 
                                detector_backend='mtcnn')
        res['stu_num'] = stu_num
        if res['verified'] == True:
            res_list.append(res)
        if temp >= 38.5:
            res['temp_check'] = False
            res['temp'] = temp
        else:
            res['temp_check'] = True
            res['temp'] = temp
    end = time.time() 
    
    # 만약 결과값이 없다면 False를 줄력해준다.
    if len(res_list) == 0:
        verified = False
        dic = {'verified': verified}
        return dic
    # 만약 True가 한개라면
    elif len(res_list) == 1:
        verified = True
        dic = {'verified': verified,'stu_num':res_list[0]['stu_num'], "time":end-start, "model":model, 'temp':temp, 'temp_check':res_list[0]['temp_check']}
        return dic
    # 만약 이미지 True가 한개 이상일 경우
    else:
        min = 0
        for order, idx in enumerate(res_list):
            if order == 0:
                min = idx['distance']
                continue
            if idx['distance'] < min:
                min = idx['distance']
        for idx in res_list:
            if idx['distance'] == min:
                verified = True
                dic = {'verified': verified,'stu_num':idx['stu_num'], "time":end-start, "model":model, 'temp':temp, 'temp_check':idx['temp_check']}
                return dic