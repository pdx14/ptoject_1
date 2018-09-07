# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 15:25:55 2018

@author: pan
"""
import pandas as pd
import os
from math import sqrt
encoding = 'latin1'

#读取数据
upath = os.path.expanduser('ml-1m/users.dat')
rpath = os.path.expanduser('ml-1m/ratings.dat')
mpath = os.path.expanduser('ml-1m/movies.dat')

unames = ['user_id', 'gender', 'age', 'occupation', 'zip']
rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
mnames = ['movie_id', 'title', 'genres']
#读取文件
users = pd.read_csv(upath, sep='::', header=None, names=unames, encoding=encoding,engine='python')
ratings = pd.read_csv(rpath, sep='::', header=None, names=rnames, encoding=encoding,engine='python')
movies = pd.read_csv(mpath, sep='::', header=None, names=mnames, encoding=encoding,engine='python')

#合并dataframe类型数据集
all_data = pd.merge(pd.merge(ratings, users), movies)

#测试
#print(all_data)

#提取数据集中所需要的列数据
umr_data = all_data[['user_id','movie_id','rating']]

#测试
#print(type(umr_data))

#将dataframe格式的数据转换为列表形式
user_id = []
movie_id = []
rating = []
for i in range(len(umr_data)):
    user_id.append(umr_data['user_id'][i])
    movie_id.append(umr_data['movie_id'][i]) 
    rating.append(umr_data['rating'][i])
    
    
#将列表数据转化为嵌套字典
dic_data = {}
#外层字典
for i in range(len(user_id)):
    a = user_id[i]
    dic_data[a] = {}
#内层字典 
for i in range(len(user_id)):
    a = user_id[i]
    b = movie_id[i]
    c = rating[i]
    dic_data[a][b] = c
#测试
#dic_data


#欧几里得算法
def sim_distance(dic, user1, user2):   
    sim = {}
    for movie_id in dic_data[user1]:
        if movie_id in dic_data[user2]:
            sim[movie_id] = 1       #添加共同项到字典中
    #无共同项，返回0
    if len(sim)==0:         
        return 0
    #计算所有共有项目的差值的平方和
    sum_all = sum([pow(dic[user1][movie_id]-dic[user2][movie_id], 2)
                   for movie_id  in sim])
    #返回改进的相似度函数
    return 1/(1+sqrt(sum_all))

#测试
#print("\n测试计算欧几里得距离的方法sim_distance()....")
#print("sim_distance(dic_data,1,2) = ",sim_distance(dic_data, 1, 2))



#皮尔逊相关度算法
def sim_pearson(dic_data, user1, user2):
    sim = {}
    #查找双方都评价过的项
    for movie_id in dic_data[user1]:
        if movie_id in dic_data[user2]:
            sim[movie_id] = 1           #将相同项添加到字典sim中
    #元素个数
    n = len(sim)
    if len(sim)==0:
        return -1
    # 所有偏好之和
    sum1 = sum([dic_data[user1][movie_id] for movie_id in sim])  
    sum2 = sum([dic_data[user2][movie_id] for movie_id in sim])  
    #求平方和
    sum1Sq = sum( [pow(dic_data[user1][movie_id] ,2) for movie_id in sim] )
    sum2Sq = sum( [pow(dic_data[user2][movie_id] ,2) for movie_id in sim] )
    #求乘积之和 ∑XiYi
    sumMulti = sum([dic_data[user1][movie_id]*dic_data[user2][movie_id] for movie_id in sim])
    num1 = n*sumMulti - (sum1*sum2)
    num2 = sqrt( (n*sum1Sq-pow(sum1,2))*(n*sum2Sq-pow(sum2,2)))
    if num2==0:
        return 0
    return num1/num2

#测试
#print("\n测试计算Pearson系数的方法sim_pearson()....")
#print("sim_pearson(dic_data,1,2) = ",sim_pearson(dic_data, 1, 2))





#获取相似用户
#K可选参数
def topMatches(dic_data, user, n=3, similarity=sim_pearson):
    ratings=[ (similarity(dic_data,user,other),other) for other in dic_data if other!=user]

    ratings.sort()    
    ratings.reverse()
    return ratings[0:5]               


##测试
#print("\n测试topMatches()方法......")
#print(topMatches(dic_data, 2))




#获取推荐
# 提供推荐，利用所有人评价的加权均值。 相似度高，影响因子越大。
def getRecommendations(dic_data, user, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in dic_data:
        if other == user:
            continue
        else:
            sim = similarity(dic_data, user, other)    #计算比较其他用户的相似度
        #相似度>0
        if sim<=0: 
            continue
        for movie_id in dic_data[other]:
            if movie_id not in dic_data[user]:
                #加权评价值：相似度*评价值
                totals.setdefault(movie_id,0)  #每轮循环开始时初始化为0
                totals[movie_id] += dic_data[other][movie_id]*sim
                #相似度之和
                simSums.setdefault(movie_id,0)
                simSums[movie_id] += sim
    #建立归一化列表
    ranks = [(total/simSums[movie_id],movie_id) for movie_id, total in totals.items() ]
    #返回经排序后的列表
    ranks.sort()
    ranks.reverse()
    return ranks[0:6]     #获取前6条电影id

##测试
#print("\n测试推荐方法getRecommendations(dic_data, user, similarity=sim_pearson)......")
#print(getRecommendations(dic_data, 1))
    


#获取用户可能喜欢的电影
total_data = getRecommendations(dic_data, 1022)
all_data_index = movies.set_index('movie_id')#在数据集中，以movie_id作为索引，来获取电影title
print("\n该用户可能喜欢的电影为）......")
for i in range(0,len(total_data)):
    print(all_data_index["title"][total_data[i][1]])
    
    